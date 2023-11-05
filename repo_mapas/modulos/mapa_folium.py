#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Sebastián RIFFO

A partir de folium, Genera un mapa de una elección de diputados o senadores,  
usando la función *mapa_elecciones_folium*. Incorpora elementos complementarios, 
a saber: 
- los marcadores asociados a cada distrito/circunscripción (y sus respectivos 
popups, que despliegan el detalle de la elección), son creados y personalizados 
usando la función *markers*. 
- Contiene un cuadro lateral, creado en función de la información disponible.
De existir datos por coalición, se forma a partir de *resultados_subdiv*; y en 
caso contrario, se crea una leyenda mediante *categorical_legend*.
- Incluye un diagrama con la composición de la cámara (elaborado en Highcharts),
por medio de la función *dist_eleccion*. 

Si bien la leyenda categórica y el diagrama no son propios de folium, pueden 
agregarse directamente al código html. En el caso del cuadro lateral con resultados
detallados, se integra por medio de *editar_template*, que modifica el template 
y agrega además otras funcionalidades. 

"""

from mapa.markers import markers
from mapa.legends import resultados_subdiv, categorical_legend
from mapa.apportionment import dist_eleccion

import folium
from folium.plugins import Geocoder
from branca.element import Template

from shapely.geometry import Point

import geopandas as gpd
import pandas as pd
import re
import webbrowser

def mapa_elecciones_folium(path_mapas, eleccion, rep, listas, candidatos, div_electoral, leyenda=None):
    """
    Mapa de una elección de diputados o senadores, a partir de 1932. Contiene 
    además un diagrama con la composición de la nueva legislatura (en el caso 
    de los senadores, incluye también a quienes estén en ejercicio); y un panel 
    lateral, que pueden ser los resultados de las principales coaliciones o una 
    leyenda categórica de estas.

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
        - legisladores electos (columns=[Candidato, Votos, Porcentaje, url])   
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

#%% GENERAR MAPA
    ## geodfs de distritos/circunscripciones
    votacion_div_electoral, lim = geodata(eleccion, rep, listas, candidatos, div_electoral)
    
    if listas is not None:
        datos_nac, datos_loc = resultados_subdiv(eleccion, rep, votacion_div_electoral, listas, leyenda)
        votacion_div_electoral['table'] = datos_loc

    ## centro (to_crs : coordinate reference system)
    lat_map, long_map = (lim['miny'].min() + lim['maxy'].max())/2, (lim['minx'].min() + lim['maxx'].max())/2 -1

    ## MAPA
    sample_map = folium.Map(location=[lat_map, long_map], zoom_start=8, minZoom = 4, maxZoom = 13, zoomSnap=0.1, zoom_control=False)
    folium.TileLayer('CartoDB positron', control=True).add_to(sample_map)
                                
    # colormap
    def color_listas(x):
        return leyenda[x] if (x in leyenda.keys()) else ('#e5e4e2' if x == 'senado' else '#a04000')

    cols_div_json = [x for x in votacion_div_electoral.columns if x != 'marker']
                
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
    
#%% customizacion
    ## construir marcadores y popups
    fg = folium.FeatureGroup(name='Electos', overlay=True, control=True)
    sample_map.add_child(fg)
    
    marker_cluster = markers(eleccion, rep, listas, candidatos, votacion_div_electoral, fg, color_listas, leyenda)

    ## distribución parlamentaria
    subdivision = votacion_div_electoral[votacion_div_electoral['Lista/Pacto'] != 'senado'].index
    
    legislatura = dist_eleccion(eleccion, rep, subdivision, candidatos, leyenda, color_listas)[0]
    sample_map.get_root().add_child(legislatura)

    ## search bar
    ## fuente : https://github.com/perliedman/leaflet-control-geocoder
    Geocoder(position='topleft', collapsed=True, add_marker=False).add_to(sample_map)

    html_to_insert = """<style>
    .leaflet-control-geocoder-icon {width: 36px !important; height: 36px !important; border-radius:3px !important;} 
    .leaflet-control-geocoder{left: 50px !important; top: 2px !important;}
    .leaflet-bar{border: 2px solid rgba(0,0,0,0.2) !important; background-clip: padding-box !important; box-shadow: none !important;}
    </style>"""

    sample_map.get_root().header.add_child(folium.Element(html_to_insert))

    ## panel lateral: leyenda categórica
    if listas is None:            
        cat_legend = categorical_legend(leyenda, listas.groupby(level=1).agg({'Electos': 'sum'}).query('Electos> 0') if (listas is not None) else candidatos.groupby(level=1).agg({'Candidatos': 'count'}))            
        sample_map.get_root().add_child(cat_legend)

    ## panel lateral : resultados detallados, listeners    
    sample_map = editar_template(sample_map, layer_dist, marker_cluster, datos_nac)

#%% GUARDAR MAPA
    if eleccion >= 1989 or eleccion == 1932:
        filename = ''.join([str(eleccion+1), '-', str(eleccion+5),{0: '_Diputados', 1: '_Senadores'}[rep],  '.html'])
    else:
        filename = ''.join([str(eleccion), '-', str(eleccion+4),{0: '_Diputados', 1: '_Senadores'}[rep], '.html'])

    sample_map.save(path_mapas/filename)
    webbrowser.open(str(path_mapas/filename))

#%%
#%% FUNCIONES VARIAS
#%%
def geodata(eleccion, rep, listas, candidatos, div_electoral):
    """
    Entrega un geodataframe creado a partir de la división electoral, al cual 
    se le agrega información complementaria.
    
    Parámetros
    ----------
    eleccion : int
        Año de la elección.
    rep : int
        Elección de diputados (0) o senadores (1).
    listas : dataframe
        Info electoral por Lista/Pacto, en cada subdivisión.      
    candidatos : dataframe 
        Info electoral de candidatos en cada subdivisión.   
    div_electoral : geodataframe
        Geometrí­as de la division electoral, a nivel nacional.   

    Entrega
    -------
    votacion_div_electoral : geodataframe 
        Contiene por columnas
        'nombre', nombre de cada distrito/circunscripción
        'geometry', geometrías respectivas
        'Lista/Pacto': coalición mayoritaria ('nacionales' y 'senado' denotan una circunscripción donde no hubo elecciones)
        'marker': posición del marcador
    
    lim : dataframe
        límites de los distritos/circunscripciones en los cuales está centrada
        inicialmente la visualización.

    """
    
    subdivrow = {0:'Distrito',1:'Circunscripción'}[rep]
    
    if rep == 0 and eleccion >= 1989:
        div_electoral[subdivrow] = div_electoral['nombre'].map(lambda x: x.split()[0])
    else:
        div_electoral[subdivrow] = div_electoral['nombre']
    div_electoral = div_electoral.reset_index().set_index(subdivrow)

    ## 
    if listas is not None:
        coalicion_max = listas.where(listas.where(listas.groupby(level=0)['Electos'].transform(lambda x: x == x.max()).astype(bool))
                                        .groupby(level=0)['Porcentaje'].transform(lambda x: x == x.max()).astype(bool)).dropna().reset_index(level=1)['Lista/Pacto']

        if (rep == 0) or (rep == 1 and candidatos.index.get_level_values(subdivrow).unique().equals(listas.index.get_level_values(subdivrow).unique()) ): 
            votacion_div_electoral = pd.merge(div_electoral, coalicion_max, left_index=True, right_index=True)
        else:            
            votacion_div_electoral = div_electoral.join(coalicion_max)
    else:
        votacion_div_electoral = pd.merge(div_electoral,
                                          candidatos.groupby(level=[0,1]).agg({'Candidatos':'count'}).groupby(level=0).transform(lambda x: x == x.max()).astype(bool).reset_index(level=1).query('Candidatos == True')['Lista/Pacto'],
                                          left_index=True, right_index=True)

    votacion_div_electoral = votacion_div_electoral[~votacion_div_electoral.index.duplicated(keep='first')]

    ## elecciones al senado
    if (rep == 1) and eleccion not in {1932, 1989}:
        mask = votacion_div_electoral['Lista/Pacto'].isna() if listas is not None else votacion_div_electoral['nombre'].str.contains('Tarapacá|Aconcagua|Colchagua|Concepción|Valdivia' +'|Chiloé'*(eleccion == 1969)).apply(lambda x: not(x) if ((eleccion-1937)%8 == 0) else x)
       
        votacion_div_electoral['Lista/Pacto'] = votacion_div_electoral['Lista/Pacto'].astype(str)
        votacion_div_electoral.loc[mask,'nombre'] = 'nacionales'            
        votacion_div_electoral.loc[mask,'Lista/Pacto'] = 'senado'

    ## posición inicial del mapa
    pos = list(filter(re.compile('|'.join(['Valparaíso', "O'Higgins"])).findall, div_electoral['nombre'])) if eleccion >= 1989 else (['Aconcagua', 'Colchagua'] if rep == 0 else ['Santiago'])
    lim = votacion_div_electoral.loc[votacion_div_electoral['nombre'].isin(pos)].to_crs("epsg:4326").bounds

    ## posición de marcadores
    votacion_div_electoral['marker'] = votacion_div_electoral['geometry'].centroid.to_crs("epsg:4326")    

    # reposicionar algunos a mano
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

    # reposicionar usando límites continentales en Valparaíso, Chiloé, Aysén y Magallanes
    marker_subdiv = ['Valparaíso', 'Chiloé', 'Aysén', 'Magallanes'] 

    if marker_subdiv:
        r = list(filter(re.compile('|'.join(marker_subdiv)).findall, votacion_div_electoral['nombre']))

        u = gpd.GeoDataFrame({'geometry': [max(votacion_div_electoral.loc[k]['geometry'].geoms, key=lambda a: a.area) if votacion_div_electoral.loc[k]['geometry'].geom_type == 'MultiPolygon' 
                                            else votacion_div_electoral.loc[k]['geometry'] for k in votacion_div_electoral[votacion_div_electoral['nombre'].isin(r)].index] 
                              })
        u = u.set_crs('epsg:3857')
        u = u.set_index([votacion_div_electoral[votacion_div_electoral['nombre'].isin(r)].index.to_list()])

        lim.loc[(u.index).intersection(lim.index)] = u.loc[(u.index).intersection(lim.index)].to_crs("epsg:4326").bounds
        votacion_div_electoral.loc[u.index,'marker'] = u.centroid.to_crs("epsg:4326")   
        
    return votacion_div_electoral[['nombre', 'geometry', 'Lista/Pacto', 'marker']], lim

#%%
def editar_template(sample_map, layer_dist, marker_cluster, datos_nac=None):
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
    datos_nac : str or None
        Tabla html con los resultados por coalición a nivel nacional.

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

    if datos_nac is not None:
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
