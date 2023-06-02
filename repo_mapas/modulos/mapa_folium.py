#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mapa de una elección de diputados o senadores, generados en folium mediante 
la función *mapa_elecciones*. 

Los marcadores asociados a cada distrito o circunscripción, al igual que la 
información electoral desplegada en los popups respectivos, son personalizados 
usando las funciones *marker_subdiv* y *popup_resultados_subdiv*. 

Un cuadro con los resultados de cada coalición se forma a partir de *resultados_subdiv*, 
de estar disponibles. Sino, se crea una leyenda mediante *categorical_legend*.

Adicionalmente, el diagrama con la composición de la cámara se genera en Highcharts,
por medio de la función *dist_eleccion*. En ella, *legislaturaBCN* agrega un 
subtí­tulo vinculado a un artí­culo de la BCN.

El cuadro lateral, leyenda y diagrama no son propios de folium. Para integrar
el primero al código html del mapa, la función *editar_template* modifica el template, 
agregando además otras funcionalidades. Los otros dos se agregan directamente
al template.

"""

import geopandas as gpd
import pandas as pd
import re
import webbrowser

import folium
from folium.plugins import MarkerCluster
from folium.plugins import Geocoder
from branca.element import Template, MacroElement

from shapely.geometry import Point

from bs4 import BeautifulSoup

from PIL import ImageFont
font = ImageFont.truetype('/usr/share/fonts/truetype/corscore/Arimo-Regular.ttf', 12)
fonttitle = ImageFont.truetype('/usr/share/fonts/truetype/corscore/Arimo-Regular.ttf', 18)

from unidecode import unidecode
from pactos import siglas_partidos

def mapa_elecciones_folium(path_mapas, eleccion, rep, listas, candidatos, div_electoral, leyenda=None):
    """
    Mapa de una elección de diputados o senadores, a partir de 1941. Contiene 
    un diagrama con la composición de la nueva legislatura (que en el caso de los senadores, 
    incluye también a quienes estén en ejercicio).

    Parámetros
    ----------
    path_mapas : PosixPath
        Directorio.
    eleccion : int
        Año de la elección.
    rep : int
        Elección de diputados (0) o senadores (1).
    listas : dataframe
        Info electoral por Lista/Pacto, en cada subdivisión.      
    candidatos : dataframe 
        Info electoral de candidatos en cada subdivisión. Distingue entre la 
        la lista completa de 
        - candidatos (columns=[Candidato, Votos, Porcentaje, Electos])
        - legisladores electos (columns=[Candidato, Votos, Porcentaje, url (opcional)])        
    div_electoral : geodataframe
        Geometrí­as de la division electoral, a nivel nacional.   
    leyenda : dict[str,str], opcional
        Nombres de listas y colores asociados, según el formato 
        {lista_1 : color_1, ... , lista_k : color_k}

    Entrega
    -------
    Mapas en formato html, guardados en path_mapas.

    """
    ## Leyenda por defecto
    if leyenda == None:
        labels = candidatos.groupby('Partido').agg({'Candidatos':'count'}) if listas == None else listas.index.levels[1][(listas.groupby(level=1)['Electos'].sum() > 5)].values.tolist()
        labels = labels.index[labels['Candidatos'] > 5].values.tolist()
        labels.append('Otros')

        # SOURCE : https://plotly.com/python/discrete-color/
        import plotly.express as px
        colors = (1 + len(labels)//11)*[x.replace(' ', '') for x in px.colors.qualitative.Pastel]
        leyenda = dict(zip(labels, colors[:len(labels)]))

    ## votacion_div_electoral : geometrías de todos los distritos/circunscripciones
    if listas is not None:
        if (rep == 0) or (rep == 1 and candidatos.index.levels[0].equals(listas.index.levels[0])):
            votacion_div_electoral = pd.merge(div_electoral,
                                              listas.where(listas.where(
                                                  listas.groupby(level=0)['Electos'].transform(lambda x: x == x.max()).astype(bool))
                                                  .groupby(level=0)['Porcentaje'].transform(lambda x: x == x.max()).astype(bool)).dropna().reset_index(level=1)['Lista/Pacto'],
                                              left_index=True, right_index=True)
        else:            
            votacion_div_electoral = div_electoral.join(listas.where(listas.where(
                                                            listas.groupby(level=0)['Electos'].transform(lambda x: x == x.max()).astype(bool))
                                                            .groupby(level=0)['Porcentaje'].transform(lambda x: x == x.max()).astype(bool)).dropna().reset_index(level=1)['Lista/Pacto']
                                                        )
    else:
        votacion_div_electoral = pd.merge(div_electoral,
                                          candidatos.groupby(level=[0,1]).agg({'Candidatos':'count'}).groupby(level=0).transform(lambda x: x == x.max()).astype(bool).reset_index(level=1).query('Candidatos == True')['Lista/Pacto'],
                                          left_index=True, right_index=True)
                
    votacion_div_electoral.index.names = ['dis_elec']
    votacion_div_electoral = votacion_div_electoral.reset_index()    
    votacion_div_electoral = votacion_div_electoral.set_index('dis_elec', drop=False)

    votacion_div_electoral = votacion_div_electoral[~votacion_div_electoral.index.duplicated(keep='first')]
                
    ## posición inicial del mapa
    pos = list(filter(re.compile('|'.join(['Valparaíso', "O'Higgins"])).findall, div_electoral['nombre'])) if eleccion >= 1989 else (['Aconcagua', 'Colchagua'] if rep == 0 else ['Santiago'])
    lim = votacion_div_electoral.loc[votacion_div_electoral['nombre'].isin(pos)].to_crs("epsg:4326").bounds

    ## posiciones de marcadores 
    votacion_div_electoral['marker'] = votacion_div_electoral['geometry'].centroid.to_crs("epsg:4326")    

    # reposicionar algunos
    marker_rep = (['D42','D57']*(rep == 0) +['Bío-Bío Costa']*(rep == 1)) if (1989 <= eleccion <= 2013) else \
                  (['Colchagua','Curicó']*(rep == 0) if (1932 <= eleccion <= 1973) else [])

    if marker_rep:
        r = list(filter(re.compile('|'.join(marker_rep)).findall, votacion_div_electoral['nombre']))

        rep_xy = {'D42': (0, 0.15), 'D57': (0, 0.15), 'Bío-Bío Costa': (-0.25,0),
                  'Colchagua': (-0.25, 0), 'Curicó': (0.25,0), 'Aysén y Magallanes': (-0.25,7.75) if eleccion <= 1965 else (2,-2.5)}        
        for s in r: 
            rep_xy[s] = rep_xy.pop([x for x in rep_xy.keys() if x in s][0])  

        mask = votacion_div_electoral['nombre'].isin(r)
        votacion_div_electoral.loc[mask,'marker'] = votacion_div_electoral[mask].apply(lambda row: Point(row['marker'].x +rep_xy[row['nombre']][0], row['marker'].y +rep_xy[row['nombre']][1]) ,axis=1)

    # usar límites continentales en Valparaíso, Chiloé, Aysén y Magallanes
    r = list(filter(re.compile('Valparaíso|Chiloé|Aysén|Magallanes').findall, votacion_div_electoral['nombre']))
    
    if r: 
        u = gpd.GeoDataFrame({'geometry': [max(votacion_div_electoral.loc[k]['geometry'].geoms, key=lambda a: a.area) if votacion_div_electoral.loc[k]['geometry'].geom_type == 'MultiPolygon' 
                                            else votacion_div_electoral.loc[k]['geometry'] for k in votacion_div_electoral[votacion_div_electoral['nombre'].isin(r)].index] 
                              })
        u = u.set_crs('epsg:3857')
        u = u.set_index([votacion_div_electoral[votacion_div_electoral['nombre'].isin(r)].index.to_list()])

        lim.loc[(u.index).intersection(lim.index)] = u.loc[(u.index).intersection(lim.index)].to_crs("epsg:4326").bounds
        votacion_div_electoral.loc[u.index,'marker'] = u.centroid.to_crs("epsg:4326")   

    ## GENERAR MAPA
    # centro (to_crs : coordinate reference system)
    lat_map, long_map = (lim['miny'].min() + lim['maxy'].max())/2, (lim['minx'].min() + lim['maxx'].max())/2 -1

    sample_map = folium.Map(location=[lat_map, long_map], zoom_start=8, minZoom = 4, maxZoom = 13, zoomSnap=0.1, zoom_control=False)
    folium.TileLayer('CartoDB positron', control=True).add_to(sample_map)

    if (rep == 1) and eleccion not in {1932, 1989}:
        mask = votacion_div_electoral['Lista/Pacto'].isna() if listas is not None else votacion_div_electoral['nombre'].str.contains('Tarapacá|Aconcagua|Colchagua|Concepción|Valdivia' +'|Chiloé'*(eleccion == 1969)).apply(lambda x: not(x) if ((eleccion-1937)%8 == 0) else x)
       
        votacion_div_electoral['Lista/Pacto'] = votacion_div_electoral['Lista/Pacto'].astype(str)
        votacion_div_electoral.loc[mask,'nombre'] = 'nacionales'            
        votacion_div_electoral.loc[mask,'Lista/Pacto'] = 'senado'
        
    ## panel derecho (tabla html)
    if listas is not None:
        debug = False  # verificar si los datos construidos coinciden
        votacion_div_electoral, datos_nac = resultados_subdiv(eleccion, rep, votacion_div_electoral, listas, leyenda, debug)
        cols_div_json = ['dis_elec', 'nombre', 'geometry', 'Lista/Pacto', 'table']
    else: 
        datos_nac = None
        cols_div_json = ['dis_elec', 'nombre', 'geometry', 'Lista/Pacto']
        
    # colormap
    def color_listas(x):
        return leyenda[x] if (x in leyenda.keys()) else ('#e5e4e2' if x == 'senado' else '#a04000')
                
    layer_dist = folium.GeoJson(votacion_div_electoral[cols_div_json],
                                name='Votación por Distrito',
                                control=True,
                                style_function=lambda x: {
                                    'color': 'black',
                                    'weight': 1,
                                    'fillColor': color_listas(x['properties']['Lista/Pacto']),
                                    'fillOpacity': 0.4},
                                highlight_function=lambda x: {
                                    'color': 'black',
                                    'weight': 2,
                                    'fillColor': color_listas(x['properties']['Lista/Pacto']),
                                    'fillOpacity': 0.6},
                                )

    sample_map.add_child(layer_dist)
    
    ## construir marcadores y pop-ups
    fg = folium.FeatureGroup(name='Electos', overlay=True, control=True)
    sample_map.add_child(fg)
    marker_cluster = MarkerCluster().add_to(fg)

    for j in votacion_div_electoral.index:
        ## MARCADORES
        escanos_subdiv = (candidatos['Electos'].loc[j] == '*').sum() if 'Electos' in candidatos.columns else (candidatos.loc[j]['Candidatos'].notna()).sum()            
        listas_subdiv = listas.loc[j]['Electos'] if (listas is not None and j in listas.index.levels[0]) else candidatos.groupby(level=[0,1]).agg({'Candidatos':'count'}).loc[j]
        
        x_loc = votacion_div_electoral['marker'].y[j] 
        y_loc = votacion_div_electoral['marker'].x[j] 

        (marker_html, marker_anchor) = marker_subdiv(escanos_subdiv, listas_subdiv, color_listas)

        ## POP-UPs : tabla de candidatos por subdivision
        popup = popup_resultados_subdiv(eleccion, rep, escanos_subdiv, candidatos, j, leyenda) 

        folium.Marker(location= [x_loc, y_loc],
                      draggable=False,
                      popup=popup,
                      icon=folium.DivIcon(html=marker_html, icon_anchor=marker_anchor)).add_to(marker_cluster)

    ## Distribución parlamentaria
    if 'Electos' in candidatos.columns:
        electos = candidatos[candidatos['Electos'] == '*']
        electos = electos.drop(['Electos'], axis=1)
    else:
        electos = candidatos

    subdivision = votacion_div_electoral[votacion_div_electoral['Lista/Pacto'] != 'senado'].index
    
    legislatura = dist_eleccion(eleccion, rep, subdivision, electos, leyenda, color_listas)
    sample_map.get_root().add_child(legislatura)

    ## SEARCH BAR
    # fuente : https://github.com/perliedman/leaflet-control-geocoder
    Geocoder(position='topleft', collapsed=True, add_marker=False).add_to(sample_map)

    html_to_insert = """<style>
    .leaflet-control-geocoder-icon {width: 36px !important; height: 36px !important; border-radius:3px !important;} 
    .leaflet-control-geocoder{left: 50px !important; top: 2px !important;}
    .leaflet-bar{border: 2px solid rgba(0,0,0,0.2) !important; background-clip: padding-box !important; box-shadow: none !important;}
    </style>"""

    sample_map.get_root().header.add_child(folium.Element(html_to_insert))

    ## PANEL DERECHO, listeners
    if listas is not None:            
        panel = True
    else:
        panel = False

        cat_legend = categorical_legend(leyenda, listas.groupby(level=1).agg({'Electos': 'sum'}).query('Electos> 0') if (listas is not None) else candidatos.groupby(level=1).agg({'Candidatos': 'count'}))            
        sample_map.get_root().add_child(cat_legend)

    sample_map = editar_template(sample_map, layer_dist, marker_cluster, datos_nac, panel)

    ## GUARDAR MAPA
    if eleccion >= 1989 or eleccion == 1932:
        filename = ''.join([str(eleccion+1), '-', str(eleccion+5),{0: '_Diputados', 1: '_Senadores'}[rep],  '.html'])
    else:
        filename = ''.join([str(eleccion), '-', str(eleccion+4),{0: '_Diputados', 1: '_Senadores'}[rep], '.html'])

    sample_map.save(path_mapas/filename)
    webbrowser.open(str(path_mapas/filename))

# %% FUNCIONES VARIAS
# %%

def marker_subdiv(escanos, listas, color_listas):
    """
    Construye un marcador que representa el número total de parlamentarios en el 
    distrito o circunscripción. Está coloreado según los escaños obtenidos por 
    cada coalición.
    
    Parámetros
    ----------
    escanos : int
        Número de escaños de la subdivisión.
    listas : dataframe
        Info electoral por Lista/Pacto, en cada subdivisión.      
    color_listas : función
        Colormap.

    Entrega
    -------
    html_marker : str
        código html asociado al marcador
    anchor : [str,str] 
        posición del marcador
    
    """    
    
    color = [color_listas(tag) for tag in listas.index for i in range(0, listas.loc[tag].sum())]

    # más de un independiente en la papeleta y al menos uno electo (las candidaturas independientes van al final)
    if(listas.index.tolist().count('Candidatura Independiente') > 1 and listas.loc['Candidatura Independiente'].sum() > 0):
        color = color[:-listas.index.tolist().count('Candidatura Independiente') +listas.loc['Candidatura Independiente'].sum()]

    stroke = ['1']*12
    width = '80'
    height = '80'

    anchor = ['40', '40']

    if escanos == 18:
        stroke = '1'
        width = '100'
        height = '100'

        anchor = [50, 50]

        html_marker = f"""
<div><svg width={width} height={height}>
    <circle cx="50.0" cy="50.0" r="8" stroke='black' stroke-width={stroke} fill={color[0]} />
    <circle cx="60.0" cy="32.7" r="8" stroke='black' stroke-width={stroke} fill={color[1]} />        
    <circle cx="40.0" cy="32.7" r="8" stroke='black' stroke-width={stroke} fill={color[2]} />        
    <circle cx="30.0" cy="50.0" r="8" stroke='black' stroke-width={stroke} fill={color[3]} />
    <circle cx="40.0" cy="67.3" r="8" stroke='black' stroke-width={stroke} fill={color[4]} />        
    <circle cx="60.0" cy="67.3" r="8" stroke='black' stroke-width={stroke} fill={color[5]} />
    <circle cx="70.0" cy="50.0" r="8" stroke='black' stroke-width={stroke} fill={color[6]} />
    <circle cx="90.0" cy="50.0" r="8" stroke='black' stroke-width={stroke} fill={color[7]} />
    <circle cx="83.5" cy="71.8" r="8" stroke='black' stroke-width={stroke} fill={color[8]} />
    <circle cx="66.3" cy="86.5" r="8" stroke='black' stroke-width={stroke} fill={color[9]} />    
    <circle cx="43.7" cy="89.5" r="8" stroke='black' stroke-width={stroke} fill={color[10]} />
    <circle cx="23.2" cy="79.7" r="8" stroke='black' stroke-width={stroke} fill={color[11]} />
    <circle cx="11.4" cy="60.4" r="8" stroke='black' stroke-width={stroke} fill={color[12]} />
    <circle cx="11.4" cy="39.6" r="8" stroke='black' stroke-width={stroke} fill={color[13]} />
    <circle cx="23.2" cy="20.3" r="8" stroke='black' stroke-width={stroke} fill={color[14]} />    
    <circle cx="43.7" cy="10.5" r="8" stroke='black' stroke-width={stroke} fill={color[15]} />            
    <circle cx="66.3" cy="13.5" r="8" stroke='black' stroke-width={stroke} fill={color[16]} />            
    <circle cx="83.5" cy="28.2" r="8" stroke='black' stroke-width={stroke} fill={color[17]} />                   
</svg></div>"""

        return html_marker, anchor
        
    elif escanos == 10:  # 3,4,3,0
        color.extend(['none']*2)
        stroke[10:] = ['0']*2
        anchor = ['40', '30']
        height = '60',
    elif escanos == 9:  # 0,4,3,2
        color.insert(0, 'none')
        color.insert(1, 'none')
        color.insert(2, 'none')
        stroke[0:3] = ['0']*3
        anchor = ['40', '50']
    elif escanos == 8:  # 2,3,2,1
        color.insert(2, 'none')
        color.insert(6, 'none')
        color.insert(9, 'none')
        color.extend(['none'])
        stroke[2], stroke[6], stroke[9], stroke[11] = '0', '0', '0', '0'
        anchor = ['30', '40']
        width = '60'
    elif escanos == 7:  # 2,3,2,0
        color.insert(2, 'none')
        color.insert(6, 'none')
        color.extend(['none']*3)
        stroke[2], stroke[6], stroke[9:] = '0', '0', ['0']*3
        anchor = ['30', '30']
        height, width = '60', '60'
    elif escanos == 6:  # 0,3,2,1
        color.insert(0, 'none')
        color.insert(1, 'none')
        color.insert(2, 'none')
        color.insert(6, 'none')
        color.insert(9, 'none')
        color.extend(['none'])
        stroke[0:3], stroke[6], stroke[9], stroke[11] = ['0']*3, '0', '0', '0'
        width = '60'
        anchor = ['30', '50']
    elif escanos == 5:  # 2,3,0,0
        color.insert(2, 'none')
        color.extend(['none']*6)
        stroke[2], stroke[6:] = '0', ['0']*6,
        height, width = '40', '60'
        anchor = ['30', '20']
    elif escanos == 4:  # 1,2,1,0
        color.insert(1, 'none')
        color.insert(2, 'none')
        color.insert(5, 'none')
        color.insert(6, 'none')
        color.extend(['none']*4)
        stroke[1:3], stroke[5:7], stroke[8:] = ['0']*2, ['0']*2, ['0']*4
        height, width = '60', '40'
        anchor = ['20', '30']
    elif escanos == 3:  # 1,2,0,0
        color.insert(1, 'none')
        color.insert(2, 'none')
        color.extend(['none']*7)
        stroke[1:3], stroke[5:] = ['0']*2, ['0']*7
        height, width = '40', '40'
        anchor = ['20', '20']
    elif escanos == 2:  # 2,0,0,0
        color.extend(['none']*10)
        stroke[2:] = ['0']*10
        anchor = ['30', '10']
        height, width = '20', '50'
    elif escanos == 1:  # 1,0,0,0
        color.extend(['none']*11)
        stroke[1:] = ['0']*11
        anchor = ['10', '10']
        height, width = '20', '30'

    if len(color) < 12:
        color.extend(['none']*(12-len(color)))

    html_marker = f"""
<div><svg width={width} height={height}>
    <circle cx="20" cy="10.00" r="8" stroke='black' stroke-width={stroke[0]} fill={color[0]} />
    <circle cx="40" cy="10.00" r="8" stroke='black' stroke-width={stroke[1]} fill={color[1]} />
    <circle cx="60" cy="10.00" r="8" stroke='black' stroke-width={stroke[2]} fill={color[2]} />
    <circle cx="10" cy="27.32" r="8" stroke='black' stroke-width={stroke[3]} fill={color[3]} />
    <circle cx="30" cy="27.32" r="8" stroke='black' stroke-width={stroke[4]} fill={color[4]} />
    <circle cx="50" cy="27.32" r="8" stroke='black' stroke-width={stroke[5]} fill={color[5]} />
    <circle cx="70" cy="27.32" r="8" stroke='black' stroke-width={stroke[6]} fill={color[6]} />        
    <circle cx="20" cy="44.64" r="8" stroke='black' stroke-width={stroke[7]} fill={color[7]} />
    <circle cx="40" cy="44.64" r="8" stroke='black' stroke-width={stroke[8]} fill={color[8]} />
    <circle cx="60" cy="44.64" r="8" stroke='black' stroke-width={stroke[9]} fill={color[9]} />    
    <circle cx="30" cy="61.96" r="8" stroke='black' stroke-width={stroke[10]} fill={color[10]} />
    <circle cx="50" cy="61.96" r="8" stroke='black' stroke-width={stroke[11]} fill={color[11]} />    
</svg></div>"""

    return html_marker, anchor

# %%

def popup_resultados_subdiv(eleccion, rep, escanos, candidatos, j, leyenda):
    """
    Código html del popup, para cada distrito o circunscripción.
    
    El popup contiene una tabla con los resultados de la elección, la cual 
    se puede ordenar usando tablesorter (Mottie's fork). El ancho de las columnas
    se calcula usando PIL. La tabla se formatea con beautifulsoup.

    Parámetros
    ----------
    eleccion : int
        Año de la elección.
    rep : int
        Elección de diputados (0) o senadores (1).
    escanos : int
        Número de escaños de la subdivisión.
    candidatos : dataframe 
        Info electoral de candidatos en cada subdivisión. Distingue entre la 
        la lista completa de 
        - legisladores electos (columns=[Candidato, Votos, Porcentaje, url (opcional)])        
        - candidatos (columns=[Candidato, Votos, Porcentaje, Electos])
    j : int
        número de la subdivisión.
    leyenda : dict[str,str]
        Nombres de listas y colores asociados, según el formato 
        {lista_1 : color_1, ... , lista_k : color_k, 'Otros' : color_o}

    Entrega
    -------
    popup : str
        Código html del popup
        
    """

    # SOURCE1: https://stackoverflow.com/questions/62789558/is-it-possible-to-change-the-popup-background-colour-in-folium
    # SOURCE2 : https://stackoverflow.com/questions/49324569/replicating-jupyter-notebook-pandas-dataframe-html-printout
    # tablesorter (sin Iframe): http://www.loyno.edu/assets/shared/js/tablesorter/docs/index.html

    if eleccion >= 1989:
        title = {0:('Diputados Distrito '+str(j)), 1:''.join(['Senadores ',str(j),'ª Circunscripción'])}[rep]
    else:
        if j >= 71:
            title = {0: 'Diputados 7ᵃ Agrupación Departamental, ', 1: 'Senadores 7ª Agrupación Senatorial, '}[rep]
            title += '2ᵒ Distrito' if(j % 10 == 2) else str(j % 10)+'ᵉʳ Distrito'
        else:
            title = {0: 'Diputados ', 1: 'Senadores '}[rep] + str(j) + {0: 'ᵃ Agrupación Departamental ', 1: 'ª Agrupación Senatorial '}[rep]

    if (rep == 1) and (candidatos.loc[j]['Votos'].sum() == 0):
        cols = ['Candidatos']
        switch = False
    elif 'Electos' in candidatos.columns:
        cols = ['Candidatos', 'Votos', 'Porcentaje', 'Electos']
        candidatos = candidatos.fillna('')        
        switch = True
    else: 
        cols = ['Candidatos', 'Votos','Porcentaje'] if eleccion >= 1973 else ['Candidatos']
        switch = False

    # como incluir los votos de lista en 1973 ? (y antes)
    table_html = candidatos[candidatos['Candidatos'].str.len() != 0].loc[j].reset_index() 

    table_html['Candidatos'] = table_html['Candidatos'].apply(' '.join)
    table_html['Lista/Pacto2'] = table_html['Lista/Pacto']
    table_html = table_html.set_index(['Lista/Pacto', 'Lista/Pacto2', 'Partido'])
    table_html = table_html[cols]

    table_soup = BeautifulSoup(table_html.to_html(justify='center', index_names=False, bold_rows=False, border=0, table_id="table"+str(j)), "html.parser")

    table_soup.find_all('th')[0].string = ''
    table_soup.find_all('th')[0]['class'] = 'coalicion1'

    table_soup.find_all('th')[1].string = 'Lista/Pacto'
    table_soup.find_all('th')[1]['class'] = 'coalicion2'

    table_soup.find_all('th')[2].string = 'Partido'
    table_soup.find_all('th')[3].string = 'Nombre'

    table_soup.find("table")['class'] = "table"+str(j) +" tablesorter"

    tr = table_soup.find_all('tr')

    rowspan = 1    
    alt = False
    l = 0
    
    for k in range(1, len(tr)):
        # url de cada parlamentario
        if 'url' in candidatos.columns and candidatos[candidatos['Candidatos'].str.len() != 0].loc[j]['url'][k-1] != "":
            new_url = table_soup.new_tag("a", href=candidatos.loc[j]['url'][k-1], target="_blank")            
            tr[k].find_all('td')[-4 if ((eleccion >= 1973) and (candidatos.loc[j]['Votos'].sum() > 0)) else -1].string.wrap(new_url)

        # bloques según lista pacto
        if 'rowspan' in tr[k].find('td').attrs.keys():
            rowspan = int(tr[k].find('td')['rowspan'])
        else:
            rowspan = 1

        if (rowspan > 1) or (tr[k].find('td').string == tr[k].find_all('td')[1].string): 
            tr[k].find_all('td')[0]['class'] = 'coalicion1'
            tr[k].find_all('td')[1]['class'] = 'coalicion2'
            alt = not alt

            span = table_soup.new_tag("span", **{"id": l, "style": ''.join(["background:", leyenda[tr[k].find('td').string] if tr[k].find('td').string in leyenda.keys() else '#a04000', ";"])})
            tr[k].find('td').string = ''
            tr[k].find('td').string.wrap(span)

            l=l+1
            
        if alt: 
            tr[k]['class'] = 'alt'
            
        if 'Electos' in candidatos.columns:
            tr[k].find_all('td')[-1]['class'] = 'electos'

    table_html = str(table_soup)

    popup_width = 31 + max(candidatos.loc[j].index.map(lambda x: font.getsize(x[1])[0]).max(), 52) +\
                    candidatos.loc[j]['Candidatos'].apply(' '.join).map(lambda x: font.getsize(x)[0]).max() + 2*13 +\
                    (120 +55)*(eleccion >= 1973)*switch + (10+20)
    popup_width = max(popup_width, fonttitle.getsize(title)[0])

    # tablesorter 
    # - demo rowspan: http://jsfiddle.net/Mottie/abkNM/14/

    popup_html = f"""
<head>
    <meta charset="utf-8">

    <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
    
    <script src="https://mottie.github.io/tablesorter/js/jquery.tablesorter.js" type="text/javascript"></script>
    <script src="https://mottie.github.io/tablesorter/js/jquery.tablesorter.widgets.js"></script> 
    
    <link href=https://mottie.github.io/tablesorter/addons/pager/jquery.tablesorter.pager.css rel="stylesheet">
    <script src=https://mottie.github.io/tablesorter/addons/pager/jquery.tablesorter.pager.js></script>

    <script src="https://mottie.github.io/tablesorter/js/parsers/parser-input-select.js"></script>    
    <script src=https://mottie.github.io/tablesorter/js/widgets/widget-output.js></script>
       
	<script id="js">
        $(function() {{
            $.tablesorter.addParser({{
                id: 'coalicion',
                is: function (s) {{
                    return false;
                }},
                format: function (s, table, cell) {{
                    var $cell = $(cell);
                    return $cell.find('id');
                }},
                type: 'text'
            }});                        
            
    		// initial sort set using sortList option
    		$("#table{j}").tablesorter({{                       
                sortInitialOrder: "desc",
                
                // parser
                headers : {{
                    0: {{ sorter: "coalicion" }},
                    1: {{ sorter: false }},
                    2: {{ sorter: "text" }},
                    3: {{ sorter: "text" }},
                    4: {{ sorter: "digit" }},
                    5: {{ sorter: "percent" }},
                    6: {{ sorter: "text" }},                    
                }},

                widthFixed : true, 
                widgets : ["filter"],
                widgetOptions : {{
                    filter_columnFilters : false,    
                    filter_cssFilter : ["filter-column","","","","","",""],
                    filter_reset : 'button.reset',
                }},
                
                debug : true
            }});
                       
            $("#table{j}").bind("sortStart", function() {{
                var hasRowspans = false;
                $('[rowspan]', this).each(function() {{
                    hasRowspans = true;
                    var rowspan = parseInt($(this).attr('rowspan'));
                    $(this).removeAttr('rowspan');
                    var trIndex = $(this).parentsUntil('table').children('tr').index($(this).parent());
                    var tdIndex = $(this).parent().children('td').index(this);
                    for (var tr = trIndex + 1; tr < trIndex + rowspan; ++tr) {{
                        var $row = $(this).parentsUntil('table').children('tr').eq(tr);
                        if (tdIndex == 0) $row.prepend($(this).clone());
                        else $row.children('td').eq(tdIndex - 1).after($(this).clone());
                    }}
                }});
                if (hasRowspans) $(this).trigger('update');
            }});
//            .bind("sortEnd",function() {{ 
//                $('table tbody tr').each(function(i,tr){{
//                    $('td:first',tr).html(i+1);
//                }});
//            }}); 


            $('button[data-filter-column]').click(function() {{
                $("#table{j}").trigger("sorton", [ [[6,0]] ]);
                
            /*** first method *** data-filter-column="1" data-filter-text="!son" add search value to Discount column (zero based index) input */
                var filters = [],
                $t = $(this),
                col = $t.data('filter-column'), // zero-based index
                txt = $t.data('filter-text') || $t.text(); // text to add to filter
            
                filters[col] = txt;
                // using "table.hasFilters" here to make sure we aren't targeting a sticky header
                $.tablesorter.setFilters( $("#table{j}"), filters, true ); // new v2.9
                
                return false;
            }});

            $('.reset').click(function() {{
                $("#table{j}").trigger("sorton", [ [[0,0]] ]);                
            }});

        }});        
    </script>
</head>
<body>
<h4>{title}</h4>
"""

    if switch:
        popup_html += """
<div class="text-center" style="text-align:center">
    <button type="button" data-filter-column="6" data-filter-text="'*'">Electos</button>
    <button type="button" class="reset">Candidatos</button>
</div>
"""

    popup_html += f"""
<h4></h4>
{table_html}

<style type="text/css">
    body {{
        min-height: 100vh;
        margin: 0;
        box-sizing: border-box;
    }}
    
    h4 {{
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;    
        text-align:center;
        margin-bottom: 5px;
    }}

    table {{
        border: none;
        border-collapse: collapse;
        border-spacing: 0;
        color: black;
        font-size: 12px;
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        table-layout: fixed;      
        
        margin-left: auto;
        margin-right: auto;
    }}
    thead {{
        border-bottom: 1px solid black;
        vertical-align: bottom;
    }}
    tr, th, td {{
        text-align: right;
        vertical-align: middle;
        padding: 0.5em 0.5em;
        line-height: normal;
        white-space: normal;
        border: none;
    }}
    th {{
        font-weight: bold;
    }}

    /* alternate rows */
    .alt {{
        background: #f5f5f5;
    }} 

    tbody:hover th[rowspan],
    tr:hover th, tr:hover td{{
        background: rgba(66, 165, 245, 0.2);
    }}
    
    span {{
        display: inline-block;
        float: left;
        height: 12px;
        width: 12px;
        border-radius: 50%;    
        margin-right: 5px;
        margin-left: 0;
        border: 1px solid #060606;
    }}       
    
    .electos{{
        text-align: right;
    }}
       
    /* filters */
    .tablesorter-filter {{
        width: 95%;
        height: inherit;
        margin: 4px;
        padding: 4px;
        background-color: #fff;
        border: 1px solid #bbb;
        color: #333;
        -webkit-box-sizing: border-box;
        -moz-box-sizing: border-box;
        box-sizing: border-box;
        -webkit-transition: height 0.1s ease;
        -moz-transition: height 0.1s ease;
        -o-transition: height 0.1s ease;
        transition: height 0.1s ease;
    }}    
    
    /* hidden rows */
    .coalicion2{{
        display: none;
        visibility: hidden;
    }} 
    .tablesorter-filter-row td:nth-child(1){{
        display: none;
        visibility: hidden;
    }}        
    .tablesorter .filter-column {{
        display: none;
        visibility: hidden;
    }} 

    /* tablesorter icons */    
    .tablesorter-header {{
        background-image: url(data:image/gif;base64,R0lGODlhFQAJAIAAACMtMP///yH5BAEAAAEALAAAAAAVAAkAAAIXjI+AywnaYnhUMoqt3gZXPmVg94yJVQAAOw==);
        background-position: center right;
        background-repeat: no-repeat;
        cursor: pointer;
        white-space: normal;
        padding: 4px 20px 4px 4px;
    }}
    .tablesorter-headerAsc {{
        background-image: url(data:image/gif;base64,R0lGODlhFQAEAIAAACMtMP///yH5BAEAAAEALAAAAAAVAAQAAAINjI8Bya2wnINUMopZAQA7);
    }}
    .tablesorter-headerDesc {{
        background-image: url(data:image/gif;base64,R0lGODlhFQAEAIAAACMtMP///yH5BAEAAAEALAAAAAAVAAQAAAINjB+gC+jP2ptn0WskLQA7);
    }}
    .tablesorter .sorter-false {{
        background-image: none;
        cursor: default;
        padding: 4px;
    }}
       
    /* rows hidden by filtering (needed for child rows) */
    .tablesorter .filtered {{
        display: none;
    }}

</style>
</body>
"""
    # notar que min-width aplica en relacion al container leaflet-popup-container
    iframe = folium.IFrame(html=popup_html, width='100%',height=(36+21*switch)+(escanos+1)*27 + 10)

    iframe_template = iframe.render()
    iframe_template = iframe_template.replace('<iframe', f'''<iframe id="{j}"''')

    popup = folium.Popup(iframe_template, min_width=popup_width, max_width=popup_width)
    return popup


# %%
# %%
def resultados_subdiv(eleccion, rep, votacion_subdiv, listas, leyenda, debug):
    """
    Para cada subdivision o a nivel nacional, se generan tablas en formato html
    con los resultados por coalición. Es necesario «editarlas» reemplazando 
    algunos string, para agregar los colores por coalición, y un separador entre 
    votaciones y estadística general.        

    Parámetros
    ----------
    eleccion : int
        Año de la elección.
    rep : int
        Elección de diputados (0) o senadores (1).
    votacion_subdiv : geodataframe
        Geometrí­as de la division electoral, más ciertos datos electorales por 
        cada subdivisión.
    listas : dataframe
        Info electoral por Lista/Pacto, en cada subdivisión.      
    leyenda : dict[str,str]
        Nombres de listas y colores asociados, según el formato 
        {lista_1 : color_1, ... , lista_k : color_k, 'Otros' : color_o}
    debug : boolean
        Agrega los votos blancos y/o nulos a las tablas.

    Entrega
    -------
    votacion_subdiv : geodataframe
        Posee una nueva columna 'table' con las tablas (formateadas en html) 
        para cada subdivisión.
    datos_nac : str
        Código html para los resultados nacionales por coalición.

    """
    subdivrow = {0: 'Distrito', 1: 'Circunscripción'}[rep]

    estadistica = [x for x in listas.index.get_level_values('Lista/Pacto').drop_duplicates().tolist() if x in['Válidamente emitidos', 'Nulos', 'Blancos', 'Blancos/Nulos','Total']]
    
    editar = dict(zip([f"""<td>{key}</td>""" for key in leyenda.keys()], [f"""<td class="coalicion"><span style='background:{leyenda[key]};'></span>{key }</td>""" for key in leyenda.keys()]))
    editar['<td>Otros</td>'] = """<td class="coalicion"><span style='background: #a04000;'></span> Otros</td>"""

    for i in range(0, len(estadistica)):
        if i == 0: 
            editar[''.join(['<tr>\n      <td>',estadistica[i],'</td>'])] = ''.join(['</tbody><tbody><tr>\n      <td class="coalicion">',estadistica[i],'</td>'])
        else:
            editar[''.join(['<td>',estadistica[i],'</td>'])] = ''.join(['<td class="coalicion">',estadistica[i], '</td>'])
    editar['<th>Lista/Pacto</th>'] = '<th class="coalicion">Coalición</th>'

    pattern = re.compile(("|".join(editar.keys())).replace('+', '\+'))  # problema con «Chile Podemos +», 2021

    # indice categorico
    cat = list(leyenda.keys())
    cat.append('Otros')
    cat.extend(estadistica)

    # TOTALES
    listas_display = listas.copy().reset_index()
    reg = []

    listas_display['Lista/Pacto'] = listas_display['Lista/Pacto'].map(lambda x: x if x in leyenda.keys() else (x if x in estadistica else 'Otros'))

    if eleccion <= 1969 and (rep == 0):
        # (santiago y nuble a veces están repetidos)
        if len(set(listas[(listas.index.get_level_values('Distrito').isin([71, 72, 73, 8])) & (listas.index.get_level_values('Lista/Pacto').isin(estadistica[-1:]))]['Votos'].values)) == 1:
            reg.extend([72, 73, 8])
        if len(set(listas[(listas.index.get_level_values('Distrito').isin([15, 16])) & (listas.index.get_level_values('Lista/Pacto').isin(estadistica[-1:]))]['Votos'].values)) == 1:
            reg.extend([16])

    # total nacional
    listas_nac = listas_display[~listas_display[subdivrow].isin(reg)].groupby('Lista/Pacto').agg({'Votos': 'sum', 'Electos': 'sum'}).reset_index()

    listas_nac['Lista/Pacto'] = pd.Categorical(listas_nac['Lista/Pacto'], categories=cat, ordered=True)
    listas_nac = listas_nac.sort_values(['Lista/Pacto'], ascending=[True]).set_index(['Lista/Pacto'])

    listas_nac['Votos'] = listas_nac['Votos'].astype(int)
    listas_nac['Porcentaje'] = (100*listas_nac['Votos']/listas_nac.loc[estadistica[-1]]['Votos']).round(2)

    listas_nac = listas_nac.reset_index()
    
    if debug:
        datos_nac = listas_nac[['Lista/Pacto', 'Votos', 'Porcentaje']].to_html(
            justify='center', index=False, bold_rows=False, border=0, table_id='info_display')
    else:        
        mask = ~((listas_nac['Lista/Pacto'] == 'Nulos') | (listas_nac['Lista/Pacto'] == 'Blancos') | (listas_nac['Lista/Pacto'] == 'Blancos/Nulos'))
        datos_nac = listas_nac[mask][['Lista/Pacto', 'Votos', 'Porcentaje']].to_html(
            justify='center', index=False, bold_rows=False, border=0, table_id='info_display')

    datos_nac = pattern.sub(lambda m: editar[m.group(0)], datos_nac)

    # totales por division electoral
    listas_reg = listas_display.groupby([subdivrow, 'Lista/Pacto']).agg({'Votos': 'sum', 'Porcentaje': 'sum', 'Electos': 'sum'}).reset_index()

    listas_reg['Lista/Pacto'] = pd.Categorical(
        listas_reg['Lista/Pacto'], categories=cat, ordered=True)
    listas_reg = listas_reg.sort_values(
        [subdivrow, 'Lista/Pacto'], ascending=[True, True]).set_index([subdivrow, 'Lista/Pacto'])

    listas_reg['Votos'] = listas_reg['Votos'].astype(int)

    
    if debug: 
        listas_reg = listas_reg.reset_index().set_index([subdivrow])
    else:        
        listas_reg = listas_reg.reset_index()
        mask = ~((listas_reg['Lista/Pacto'] == 'Nulos') | (listas_reg['Lista/Pacto'] == 'Blancos') | (listas_reg['Lista/Pacto'] == 'Blancos/Nulos') )
        
        listas_reg = listas_reg[mask].set_index([subdivrow])

    datos = []

    for i in votacion_subdiv.index.unique():# listas_reg.index.unique():
        datos.append(pattern.sub(lambda m: editar[m.group(0)], 
                                 listas_reg.loc[i][['Lista/Pacto', 'Votos', 'Porcentaje']].to_html(justify='center', index=False, bold_rows=False, border=0, table_id='info_display')) if i in listas_reg.index else datos_nac
                     )
    votacion_subdiv['table'] = datos

    return votacion_subdiv, datos_nac

# %%

def editar_template(sample_map, layer_dist, marker_cluster, datos_nac, panel):
    """
    Hackea el template original para :
        - agregar un panel lateral con los resultados por coalición,
        - poner el zoom en la esquina superior derecha,
        - agregar listeners a cada polígono (para la versión móvil)
        - adaptar el ancho de los popups, cambiar la opacidad de los controles (para la versión móvil)

    Parámetros
    ----------
    sample_map : folium map
        Mapa generado por folium.
    layer_dist : GeoJson
        Polígonos dibujados en el mapa.
    marker_cluster : marker cluster
        Marcadores agrupados en un solo objeto.
    datos_nac : str
        Tabla html con los resultados por coalición a nivel nacional.
    panel : bool
        Indica si los datos electorales por lista están disponibles.

    Entrega
    -------
    sample_map : folium map
        Mapa cuyo template fue modificado para agregar los elementos listados.

    """

    # SOURCE : https://leafletjs.com/examples/choropleth/

    map_id = '#map_'+sample_map._id
    geojson_id = 'geo_json_'+layer_dist._id
    marker_cluster_id = 'marker_cluster_'+marker_cluster._id

    # SOURCE : https://github.com/python-visualization/folium/issues/781
    html_source = sample_map.get_root().render()

    if panel == True:
        # customizar el panel
        u = f"""                {map_id} {{
                    position: relative;
                    width: 100.0%;
                    height: 100.0%;
                    left: 0.0%;
                    top: 0.0%;
                }}"""
        v = f"""                {map_id} {{
                    position: relative;
                    width: 100.0%;
                    height: 100.0%;
                    left: 0.0%;
                    top: 0.0%;
                }}
    
                .leaflet-bottom.leaflet-left {{ 
                    position: absolute; 
                    bottom: 10px; 
//                    right: 10px; 
//                    left: 10px;                
                }}
                   
                .info {{ 
                    border:2px solid grey; 
                    background-color:rgba(255, 255, 255, 0.9);
                    border-radius:6px; 
                    padding: 10px; 
                    font-size:14px;                                  
                    
					display: flex;
					flex-direction: column;
					align-items: center; 
					justify-content: center;
                    
                    width: 500px;
                }} 
                .info h4 {{ 
                    margin: 0 0.2em 5px; 
                    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
//                    font-weight: bold;                    
                    }}
                                
                .dataframe table {{
                    border: none;
                    border-collapse: collapse;
                    border-spacing: 0;
                    color: black;
                    font-size: 14px;
                    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
                    table-layout: fixed;
                }}
                .dataframe tbody {{
                    border-top: 1px solid black;
                    vertical-align: bottom;
                }}                
                .dataframe tr, th, td {{
                    text-align: right;
                    vertical-align: middle;
                    padding: 0.2em 0.5em;
                    line-height: normal;
                    white-space: normal;
                    max-width: none;
                    border: none;
                }}
                .dataframe th {{
                    font-weight: bold;
                }}     
                
                .dataframe span {{
                    display: block;
                    float: left;
                    height: 14px;
                    width: 14px;
                    -webkit-border-radius: 7px;
                    -moz-border-radius: 7px;
                    border-radius: 7px;    
                    margin-right: 5px;
                    margin-left: 0;
                    border: 1px solid #060606;
                }}        
                
                .dataframe .coalicion{{
                    text-align: left;
                    vertical-align: middle;
                    padding: 0.2em 0.5em;
                    line-height: normal;
                    white-space: normal;
                    max-width: none;
                    border: none;
                }}"""
        html_source = html_source.replace(u, v)

        # agregar el panel, topright zoom
        map_id = 'map_'+sample_map._id
        u = f"""        function {geojson_id}_styler(feature) {{
"""
        v = f"""  
			var width = window.visualViewport.width;
			var ua = navigator.userAgent;
			var isMobile = /Android|webOS|iPhone|iPad|iPod/i.test(ua);			
			
			if (isMobile && width < 600) {{
				{map_id}.setZoom(5);
			}};    
       
            const info = L.control();
            info.setPosition('bottomleft');
    
    		info.onAdd = function (map) {{
    			this._div = L.DomUtil.create('div', 'info');
    			this.update();
    			return this._div;
    		}};
    
    		info.update = function (props) {{
    			const contents = props ? `${{props['table']}}` : `{datos_nac}`;
    
    			this._div.innerHTML = props ? `<h4>Resultados ${{props['nombre']}} </h4>${{contents}}` : `<h4>Resultados nacionales </h4>${{contents}}`;
    		}};
    
    		info.addTo({map_id});
            
            // problema con margin y dejar tabla al centro
			$(document).ready(function() {{
				if(520 > window.visualViewport.width){{
					document.getElementsByClassName('info')[0].style.width = window.visualViewport.width -20 + 'px';
				}}
			}});                       
            
            var selected = false;

			L.control.zoom({{
				position: 'topright'
			}}).addTo({map_id});            
        
        function {geojson_id}_styler(feature) {{
"""
        html_source = html_source.replace(u, v)

        # cambiar los listeners
        html_source = html_source.replace('''
                mouseout: function(e) {
                    if(typeof e.target.setStyle === "function"){''', f'''
                click: function(e) {{		
                    selected = true;
                    
                    info.update(layer.feature.properties);
					
                    {geojson_id}.resetStyle();					
														
                    const highlightStyle = {geojson_id}_highlighter(e.target.feature) 
                    e.target.setStyle(highlightStyle);
                    
                    L.DomEvent.stopPropagation(e);
                }},

                mouseout: function(e) {{
                    if(typeof e.target.setStyle === "function"){{
                        selected = true;                            
                            
                        info.update();''')

        html_source = html_source.replace('''
                mouseover: function(e) {
                    if(typeof e.target.setStyle === "function"){''',
                                          '''
                mouseover: function(e) {
                    if(typeof e.target.setStyle === "function"){
                        selected = true;
                            
                        info.update(layer.feature.properties);''')

        # adaptar ancho de popup en mobile
        # esconder geocoder : https://github.com/Leaflet/Leaflet/issues/4811
        html_source = html_source.replace('''
            L.Control.geocoder(''', f'''
		{marker_cluster_id}.addEventListener("click", myFunction);
        
		function myFunction(e) {{
 			var container = document.getElementsByClassName("leaflet-popup-content")[0]
		
 			if (container.clientWidth +40> window.visualViewport.width){{
				container.style.cssText = `width: ${{window.visualViewport.width-20}}px !important; max-height: 425px !important; overflow-y: auto !important; margin: 5px !important;` ;
 			}}
		}}
		
        var layermarker = {{}}
		Object.keys({geojson_id}._layers).forEach(function(key) {{
			layermarker[{geojson_id}._layers[key].feature.id] =  key;
		}})  
		       
		const leafletTopElements = document.querySelectorAll('div.leaflet-top');
		var x = document.getElementsByClassName('button1')[0];    
        
		{map_id}.on('popupopen', function(e) {{
			var layer = e.sourceTarget._layers[layermarker[e.target._popup._content.children[0].id]];
				
            info.update(layer.feature.properties);

            {geojson_id}.resetStyle();

			const highlightStyle = {geojson_id}_highlighter(layer.feature) 
			layer.setStyle(highlightStyle);
                        
            selected = true;
            
			leafletTopElements.forEach(function(element) {{
				element.style.opacity = 0;
			}});
			x.setAttribute("hidden", "hidden");            
		}});		
        
		{map_id}.on('popupclose', function(e) {{
			leafletTopElements.forEach(function(element) {{
				element.style.opacity = 1;
			}});
			x.removeAttribute("hidden");            
		}});
        
		{map_id}.on('click', function(e){{
			if(selected){{
				{geojson_id}.resetStyle();		
				info.update();
			}}
		}});
        
    		$('.leaflet-control-attribution').html('<a href="https://sebastianriffo.github.io/" style="color:#E91E63" target="_blank">Sebastián RIFFO</a></a> | <a href="https://leafletjs.com" title="A JS library for interactive maps"> Leaflet</a>, <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors <a href="http://cartodb.com/attributions">CartoDB</a>, <a href="https://www.highcharts.com/">Highcharts</a>')		        
                               
            L.Control.geocoder(''')
    else:
        # control zoom topright
        map_id = 'map_'+sample_map._id
        u = f"""        function {geojson_id}_styler(feature) {{
"""
        v = f"""  
			var width = window.visualViewport.width;
			var ua = navigator.userAgent;
			var isMobile = /Android|webOS|iPhone|iPad|iPod/i.test(ua);			
			
			if (isMobile && width < 600) {{
				{map_id}.setZoom(5);
			}};    
        
			L.control.zoom({{
				position: 'topright'
			}}).addTo({map_id});            
        
        function {geojson_id}_styler(feature) {{
"""
        html_source = html_source.replace(u, v)

        # adaptar ancho de popup en mobile
        # esconder geocoder : https://github.com/Leaflet/Leaflet/issues/4811
        html_source = html_source.replace('''
            L.Control.geocoder(''', f'''
		{marker_cluster_id}.addEventListener("click", myFunction);
        
		function myFunction(e) {{
 			var container = document.getElementsByClassName("leaflet-popup-content")[0]
		
 			if (container.clientWidth +40> window.visualViewport.width){{
				container.style.cssText = `width: ${{window.visualViewport.width-20}}px !important; max-height: 425px !important; overflow-y: auto !important; margin: 5px !important;` ;
 			}}
		}}
		
        var layermarker = {{}}
		Object.keys({geojson_id}._layers).forEach(function(key) {{
			layermarker[{geojson_id}._layers[key].feature.id] =  key;
		}})  
		       
		const leafletTopElements = document.querySelectorAll('div.leaflet-top');
		var x = document.getElementsByClassName('button1')[0];    
        
		{map_id}.on('popupopen', function(e) {{
			leafletTopElements.forEach(function(element) {{
				element.style.opacity = 0;
			}});
			x.setAttribute("hidden", "hidden");            
		}});		
        
		{map_id}.on('popupclose', function(e) {{
			leafletTopElements.forEach(function(element) {{
				element.style.opacity = 1;
			}});
			x.removeAttribute("hidden");            
		}});
    
    		$('.leaflet-control-attribution').html('<a href="https://sebastianriffo.github.io/" style="color:#E91E63" target="_blank">Sebastián RIFFO</a></a> | <a href="https://leafletjs.com" title="A JS library for interactive maps"> Leaflet</a>, <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors <a href="http://cartodb.com/attributions">CartoDB</a>, <a href="https://www.highcharts.com/">Highcharts</a>')		
		                               
            L.Control.geocoder(''')

    sample_map.get_root()._template = Template(html_source)

    return sample_map

# %%

def categorical_legend(leyenda, listas_nac):
    """
    Leyenda categórica.
    Fuente : https://github.com/mrcagney/examples_folium/blob/develop/notebooks/categorical_legend.ipynb

    Parámetros
    ----------
    leyenda : dict[str,str]
        Nombres de listas y colores asociados, según el formato 
        {lista_1 : color_1, ... , lista_k : color_k, 'Otros' : color_o}
    listas_nac : dataframe
        Resultados de listas a nivel nacional.

    Entrega
    -------
    macro : macroElement 
        Elemento en branca, contiene el código html de la leyenda.

    """

    # draggable legend
    # SOURCE : https://nbviewer.org/gist/talbertc-usgs/18f8901fc98f109f2b71156cf3ac81cd
    legenda_ul = ''.join([f"""<li><span style='background:{leyenda[key]};'></span>{key}</li> \n""" for key in leyenda.keys(
    ) if (key in listas_nac.index)])

    if not listas_nac[~listas_nac.index.isin(list(leyenda.keys()))].empty:
        legenda_ul += f"""<li><span style='background:{'#a04000'};'></span>{'Otros'}</li> \n"""

    leyenda_html = f"""
{{% macro html(this, kwargs) %}}

<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
    
    <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
    <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
    
    <script>
        $( function() {{
            $( "#maplegend" ).draggable({{
                start: function (event, ui) {{
                    $(this).css({{
                        left: "auto",
                        top: "auto",
                        bottom: "auto"
                    }});
                }}
            }});
        }});
    </script>
  
    <style type='text/css'>
      .maplegend .legend-title {{
        text-align: left;
        margin-bottom: 5px;
        font-weight: bold;
        font-size: 100%;
        }}
      .maplegend .legend-scale ul {{
        margin: 0;
        margin-bottom: 5px;
        padding: 0;
        float: left;
        list-style: none;
        }}
      .maplegend .legend-scale ul li {{
        font-size: 100%;
        list-style: none;
        margin-left: 0;
        line-height: 18px;
        margin-bottom: 2px;
        }}
      .maplegend ul.legend-labels li span {{
        display: block;
        float: left;
        height: 14px;
        width: 14px;
        -webkit-border-radius: 7px;
        -moz-border-radius: 7px;
        border-radius: 7px;    
        border: 1px solid #060606;
        margin-right: 5px;
        margin-left: 0;
        }}
      .maplegend .legend-source {{
        font-size: 100%;
        color: #777;
        clear: both;
        }}
      .maplegend a {{
        color: #777;
        }}
    </style> 
</head>

<body>
    <div id='maplegend' class='maplegend' 
        style='position: absolute; z-index:9997; 
        border:2px solid grey; 
        background-color:rgba(255, 255, 255, 0.9);
        border-radius:6px; padding: 10px; 
        font-size:14px; 
        left: 10px; bottom: 20px;'>
         
        <div class='legend-title'>Coaliciones</div>
        <div class='legend-scale'>
            <ul class='legend-labels'> {legenda_ul} </ul>
        </div>
    </div> 
</body>

</html>

{{% endmacro %}}"""

    macro = MacroElement()
    macro._template = Template(leyenda_html)

    return macro

# %%
# %%

def dist_eleccion(eleccion, rep, subdivision, electos, leyenda, color_listas):
    """
    Diagrama con la composición de la nueva legislatura, creado en Highcharts.

    Parámetros
    ----------
    eleccion : int
        Año de la elección.
    rep : int
        Elección de diputados (0) o senadores (1).
    electos : dataframe 
        La lista completa de los legisladores electos.
    leyenda : dict[str,str]
        Nombres de listas y colores asociados, según el formato 
        {lista_1 : color_1, ... , lista_k : color_k, 'Otros' : color_o}
    color_listas : funcion
        Colormap (definido en mapa_elecciones, línea 151)

    Entrega
    -------
    macro : MacroElement
        Elemento en branca, cuyo template es el código html del diagrama antes 
        mencionado.

    """
    import math

    # SOURCE : https://jsfiddle.net/gh/get/library/pure/highcharts/highcharts/tree/master/samples/highcharts/series-item/dynamic
    data_chart = electos.copy()[['Candidatos']].reset_index()
    """
    PARTE 1 : VALORES A USAR EN HIGHCHARTS
    En el template html se incorpora un elemento Highcharts.chart, a fin de 
    crear el diagrama. Este requiere como mínimo los siguientes valores (que 
    van en el atributo «series») para cada partido
        - name : nombre, 
        - y : número de electos,
        - color : el asociado a su pacto, según la leyenda, 
        - label : pacto al que pertenece, según la leyenda.

    Adicionalmente, agregué
        - legendIndex : transformación de los índices asociados a cada leyenda 
        en el diagrama, de modo que aparezcan en vertical y no en horizontal.        
        - additionalInfo : string con la lista de parlamentarios electos por 
        partido, para usar en un tooltip.

    Así, la información presente en electos se formatea y se guarda en data_chart.
    """

    # tooltip (SOURCE : https://www.highcharts.com/forum/viewtopic.php?f=9&t=44711)
    def tooltip_partido(x):
        return '<div style="column-count:'+str(len(x)//((rep == 0)*(20 if len(x) < 60 else 30) + (rep == 1)*10) + 1)+'">' + '<br>'.join(x) + '</div>'

    data_chart['Candidatos'] = data_chart['Candidatos'].map(lambda y: ('Ma. ' if (unidecode(y[0]) == 'Maria' and len(y) > 3) else y[0]+' ') + (len(y) >= 3 and y[1] != y[-2])*(unidecode(y[0]) in {'Juan', 'Maria', 'Jose'})*(y[1]+' ') + (y[-2] if len(y) > 2 else y[1])
                                                            ).to_frame()

    if rep == 1:        
        mask = (~data_chart['Circunscripción'].isin(subdivision)) & (data_chart['Circunscripción'] != 101)
        data_chart.loc[mask,'Candidatos'] = '* ' + data_chart[mask]['Candidatos']
        data_chart.loc[data_chart['Circunscripción'] == 101, 'Candidatos'] = '** ' + data_chart[data_chart['Circunscripción'] == 101]['Candidatos']

    # senadores : separar los electos (subdivision) de los ya instalados y designados (circ. 101)
    data_chart['Electos_total'] = 1
    data_chart['Electos_periodo'] = 1

    if rep == 1:
        data_chart.loc[(~data_chart['Circunscripción'].isin(subdivision)) | (data_chart['Circunscripción'] == 101), 'Electos_periodo'] = 0
        data_chart['Circunscripción'] = pd.Categorical(data_chart['Circunscripción'], categories=(subdivision.tolist() +[x for x in electos.index.levels[0] if x not in subdivision.tolist()]), ordered=True)
        data_chart = data_chart.sort_values(['Circunscripción'],ascending=[True])

    data_chart = data_chart.drop({0: 'Distrito', 1: 'Circunscripción'}[rep], axis=1)

    # dividir en : independientes dentro de lista, listas de partidos, candidaturas independientes
    data_chart = pd.concat([data_chart[(data_chart['Lista/Pacto'] != 'Candidatura Independiente') & (data_chart['Partido'] == 'IND')].groupby('Lista/Pacto').agg({'Partido': 'first', 'Candidatos': lambda x: tooltip_partido(x), 'Electos_total': 'sum', 'Electos_periodo': 'sum'}).reset_index().set_index('Partido'),
                            data_chart[data_chart['Partido'] != 'IND'].groupby('Partido').agg({'Lista/Pacto': 'first', 'Candidatos': lambda x: tooltip_partido(x), 'Electos_total': 'sum', 'Electos_periodo': 'sum'}),
                            data_chart[data_chart['Lista/Pacto'] == 'Candidatura Independiente'].groupby('Partido').agg({'Lista/Pacto': 'first', 'Candidatos': lambda x: tooltip_partido(x), 'Electos_total': 'sum', 'Electos_periodo': 'sum'})
                            ]).reset_index()

    data_chart = data_chart.dropna()

    # coaliciones tal como en leyenda
    # partidos ordenados en decreciente por coalición
    cat = list(leyenda.keys())
    cat.append('Otros')

    data_chart['Lista/Pacto'] = data_chart['Lista/Pacto'].map(lambda x: x if x in leyenda.keys() else 'Otros')
    data_chart['Lista/Pacto'] = pd.Categorical(data_chart['Lista/Pacto'], categories=cat, ordered=True)
    data_chart = data_chart.sort_values(['Lista/Pacto', 'Electos_total'], ascending=[True, False])

    # nombre en tooltip
    siglas = siglas_partidos()
    siglas_inv = {v: k for k, v in siglas.items()}    
    
    data_chart['Partido_tooltip'] = data_chart['Partido'].map(lambda x: x + ' ('+siglas_inv[x]+')')

    if rep == 1 and eleccion not in {1932, 1989}: 
        mask = ~data_chart['Partido'].str.contains("COSENA|SUPREMA|GOB|VIT")
        data_chart.loc[mask, 'Partido'] = data_chart.loc[mask, 'Partido'] + data_chart.loc[mask, 'Electos_periodo'].astype(str).map(lambda x: ' ('+x+')')

    data_chart['Candidatos'] = data_chart['Candidatos'].apply(lambda x: x + ('<br>* electos en el período anterior' if re.search('\>\*\s[A-Z]',x) else '') +('<br>** designados o vitalicios' if re.search('\>\*\*\s[A-Z]',x) else ''))
    
    data_chart['color'] = data_chart['Lista/Pacto'].map(lambda x: color_listas(x))

    # alineación vertical de leyendas (SOURCE : http://jsfiddle.net/1kep8yvm/)
    l = len(data_chart)
    n = 2 if l <= 10 else 3
    data_chart['legendIndex'] = [i+(j-1)*n for i in range(1, n+1) for j in range(1, l//n + (i <= l % n) + 1)]

    # tooltip en legend
    data_chart['idx'] = [i for i in range(1, l+1)]
    data_chart['tooltip'] = data_chart['idx'].map(lambda x: data_chart[data_chart['legendIndex'].isin([x])]['idx'].values[0] - 1)

    data_chart = data_chart[['Partido', 'Partido_tooltip', 'Electos_total', 'color','Lista/Pacto', 'legendIndex', 'tooltip', 'Candidatos']]

    """
    PARTE 2: PARÁMETROS
    Personalización del diagrama. El cuociente legend_width/legend_itemWidth
    sirve para regular el número de columnas. 
    """
    title_text = {0: 'Cámara de '+(eleccion >= 2021)*'Diputadas y ' +'Diputados', 1: 'Senado de la República'}[rep]
    subtitle_text = legislaturaBCN(eleccion)

    container_width = 500

    chart_height = (rep == 0)*(300 -25*max(0,min(3,math.ceil(l/n)-4))) + (rep == 1)*250
    chart_marginBottom = min(125,20*(math.ceil(l/n))+10) if math.ceil(l/n) <= 7 else 150

    container_height = chart_height + chart_marginBottom

    legend_width = 425 + (rep == 1)*75 - 180*(n < 3)
    legend_itemWidth = legend_width//n
    legend_x = 20 + 10*(n < 3)
    
    legend_width_mobile = legend_width if n < 3 else 340
    legend_itemWidth_mobile = legend_itemWidth if n < 3 else 113
    legend_x_mobile = legend_x if n < 3 else 0


    series_name = str('Diputados obtenidos'*(rep == 0) +'Senadores obtenidos'*(rep == 1))
    series_data = data_chart.values.tolist()
    series_startAngle = -(90 - 15*(rep == 1)*(2005 <= eleccion <= 2013))
    series_endAngle = -series_startAngle

    # TEMPLATE
    # visibilidad : http://jsfiddle.net/archerabi/vnBsx/1/
    # update en tamaño : http://jsfiddle.net/rqoxmc39/1/
    # tooltip en leyenda : http://jsfiddle.net/highcharts/5V33F/ y http://jsfiddle.net/8T7Ew/

    chart = f"""
{{% macro html(this, kwargs) %}}

    <script src="https://code.highcharts.com/highcharts.js"></script>
    <script src="https://code.highcharts.com/modules/item-series.js"></script>
    <script src="https://code.highcharts.com/modules/accessibility.js"></script>

    <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
    <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
    <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>    
       
    <style type='text/css'>
        .button1 {{
			background: white url(https://cdn-icons-png.flaticon.com/32/8188/8188509.png) no-repeat;			            			
			background-position: 2px center;			

            width: 40px; 
            height: 40px;
            padding: 1px;

            border-radius:4px; 
                        
            border: 2px solid rgba(0,0,0,0.2);
            background-clip: padding-box;
       }}
        
        .highcharts-tooltip {{
          pointer-events: all !important;
        }}
    </style>    

    <div id='container'
        style='position: absolute; z-index:9990; width:{container_width}px; height:{container_height}px; left: 10px; top:10px; visibility: visible;'>    
    </div>

    <button id="button" class='button1' style='position: absolute; z-index:9991; left: 12px; top:12px;'></button>    

    <script>            
    Highcharts.setOptions({{
        chart: {{
            style: {{
                fontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif',
            }}
        }}
    }});    
    
    var chart = new Highcharts.Chart('container', {{
    chart: {{
        type: 'item',
        height: '{container_height}',
        marginTop: 30,
        marginBottom: {chart_marginBottom},
        marginLeft: 10,        
        marginRight: 10,        
        backgroundColor: 'rgba(255, 255, 255, 1)',
        borderWidth: 2,
        borderRadius: 6,
        borderColor: '#808080',
    }},
    
    title: {{
        text: '{title_text}',
        style: {{
            fontWeight: 'bold',
            fontSize: '16px'
        }}
    }},

    subtitle: {{
        text: '{subtitle_text}',
        style: {{
            fontWeight: 'lighter',
            fontSize: '12px' 
        }}
    }},

	credits: {{
        enabled: false, 
    }},    
      
    legend: {{
        enabled: true,
        floating: true,
        width: {legend_width},
        itemWidth: {legend_itemWidth},
        x: {legend_x},
        labelFormat: '{{name}} <span style="opacity: 0.4">{{y}}</span>',
        itemStyle: {{
            fontWeight: 'normal',
            fontSize: '12px'
        }}
    }},

    plotOptions: {{
        series: {{
			enableMouseTracking: false,
			            
            point: {{
                events: {{
					legendItemClick: function(e) {{
                        e.preventDefault();

  						this.series.chart.update({{
  							tooltip: {{
  								enabled: true,
  							}},
  						}});

                        chart.tooltip.refresh(this);    						
                        chart.tooltip.hide(5000);
                        
                        // true: se esconden los datos
						return false;
                    }},                    
                }}
            }}
        }}
    }},

    tooltip: {{
        enabled: true,
        useHTML: true,
//        pointFormat: '<span style="color:{{point.color}}">●</span> {{series.name}} : <b>{{point.y}}</b><br/> {{point.additionalInfo}}',
        formatter: function () {{
                        return '<div style="z-index: 9992; overflow-y: auto; max-height: 300px;"> <span class="comment-trigger" style="color:'+ this.point.color +'">●</span> '+this.point.name2+ '<br/>'+this.point.additionalInfo +'</div>';
                    }},
		positioner: function () {{
    					return {{ x: 5, y: 50 }};
					}},
    }},

    series: [{{
        name: '{series_name}',
        keys: ['name', 'name2', 'y', 'color', 'label','legendIndex', 'tooltip', 'additionalInfo'],
        data: {series_data},
        dataLabels: {{
            enabled: false,
            format: '{{point.label}}'
        }}, 
        showInLegend: true,
        cursor: 'pointer',        
        point: {{
            events: {{
                click: function() {{
                    this.series.chart.update({{
                        tooltip: {{
                            enabled: false
                        }}
                    }});
                }},
                
                mouseOut: function() {{
                    this.series.chart.update({{
                        tooltip: {{
                            enabled: false
                        }}
                    }})
                }}
            }}
        }},        
        
        // Circular options
        center: ['50%', '90%'],
        size: '150%',
        startAngle: {series_startAngle},
        endAngle: {series_endAngle}
    }}],

    responsive: {{
        rules: [{{
            condition: {{
                maxWidth: 430
            }},
            chartOptions: {{
                legend: {{
                    width: {legend_width_mobile},
                    itemWidth: {legend_itemWidth_mobile},
                    x: {legend_x_mobile},
                }},
                series : [{{
                    size: '110%'
                }}]
            }}
        }}]
    }}
    
    }});

    // tooltip al clickear leyenda	
    // podria ser util para modificar opacidad en mobile
//	$('#container .highcharts-legend text, #container .highcharts-legend span').each(function(index, element) {{			
//		$(element).click(function() {{
//			legendIndex = chart.series[0].data[index].tooltip;
//			chart.tooltip.refresh(chart.series[0].data[legendIndex]);		
//		}})		
// 	}})
 	
    // esconder boton en tooltip            
//    var timeoutHandle = 0
//    var x = document.getElementsByClassName('button1')[0];    
//	
//	$(document).on('click tap touchstart','.highcharts-legend-item', function(e) {{
//		x.setAttribute("hidden", "hidden");
//		
//		function dummy(x){{
//			x.removeAttribute("hidden")
//		}};
//		clearTimeout(timeoutHandle);
//		timeoutHandle = setTimeout(dummy, 5000, x);		
//    }});                    
 	
    // esconder highcharts en mobile
    var y = document.getElementById('container');
    
    if(window.visualViewport.width > 950) {{
		y.style.visibility == 'visible'
	}} else {{
		y.style.visibility ='hidden';
    }}    

    // reajustar en click 
    $('#button').click(function() {{
        var x = document.getElementById('container')
        
        if (x.style.visibility == 'hidden') {{                                              
            x.style.width = window.visualViewport.width > 520 ? 500 + 'px' : window.visualViewport.width -20 + 'px';
            chart.reflow();
                       
            x.style.visibility ='visible';
            $('#container').find('.highcharts-legend').show();    
            
        }} else {{
            x.style.visibility ='hidden';
            $('#container').find('.highcharts-legend').hide();
        }}            
        
    }});
            
    // reajustar altura    
    if (window.visualViewport.height <= 650){{        
        var w = document.getElementById('container')        
        w.style.height = {container_height-50}+'px'

        chart.reflow();                
        chart.update({{
            chart: {{
                height: '{container_height-50}'
            }}
        }});
    }}
        
    </script>
    
{{% endmacro %}}"""

    macro = MacroElement()
    macro._template = Template(chart)

    return macro


def legislaturaBCN(eleccion):
    """
    Entrega el titulo y link de la legislatura según el año de la elección parlamentaria.

    Parámetros
    ----------
    eleccion : int
        Año de la elección.

    Entrega
    -------
    title : str
        Tí­tulo con link de la BCN correspondiente a la elección.

    """
    # fuente : https://www.bcn.cl/historiapolitica/elecciones

    p = (eleccion >= 1989)*((eleccion-1989)//4 + 48) +\
        (1937 <= eleccion <= 1973)*((eleccion-1937)//4 + 38) +\
        (1930 <= eleccion <= 1932)*((eleccion-1930)//2 + 36) +\
        (1925 <= eleccion <= 1929)*(35) +\
        (1834 <= eleccion <= 1924)*((eleccion-1834)//3 + 4) +\
        (1828 <= eleccion <= 1832)*((eleccion-1828)//2 + 1)

    u = p % 10
    d = p//10

    leg = (['X', 'XX', 'XXX', 'IL', 'L', 'LX', 'LXX', 'LXXX', 'IC'][d-1] if d > 0 else '') +\
            (['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX'][u-1] if u > 0 else '')

    # BCN : 26/10/2022
    url = 'https://www.bcn.cl/historiapolitica/elecciones/detalle_eleccion?handle=10221.1/'
    if 1989 <= eleccion <= 2021:  
        url += str( (63200+[10, 11, 12, 13, 16, 17, 23][(eleccion-1989)//4]) if eleccion <= 2013 else [87409,87444][(eleccion-2017)//4] ) + '&periodo=' + ('1973-1990' if eleccion == 1989 else '1990-2022')
        title = '<a href='+url+' target="_blank">' + leg + ' Período Legislativo ('+str(eleccion+1) + '-'+str(eleccion+5)+')' + '</a>'
    elif 1937 <= eleccion <= 1973:
        url += str(63000+[-13, -8, -6, 34, 44, 45, 64, 73, 89, 135][(eleccion-1937)//4]) + '&periodo=1925-1973'
        title = '<a href='+url+' target="_blank">' + leg + ' Período Legislativo ('+str(eleccion)+'-' + str(eleccion+4)+')' + '</a>'
    elif 1932: 
        url += '62982&periodo=1925-1973'
        title = '<a href='+url+' target="_blank">' + leg + ' Período Legislativo ('+str(eleccion+1)+'-' + str(eleccion+5)+')' + '</a>'
    else:
        title = leg + ' Perí­odo Legislativo ('+str(eleccion+1)+'-'+str(eleccion+5)+')'

    return title
