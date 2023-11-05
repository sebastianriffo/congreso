#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Sebastián RIFFO

Funciones para crear un cuadro lateral.
- *resultados_subdiv*: de existir resultados detallados, entrega tablas en html con
los resultados nacionales y locales.
- *categorical_legend*: produce una leyenda categórica

"""
from branca.element import Template, MacroElement

import pandas as pd
import re

def resultados_subdiv(eleccion, rep, votacion_subdiv, listas, leyenda):
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

    Entrega
    -------
    datos_nac : str
        Código html para los resultados nacionales por coalición.
    datos_rec : str
        Código html para los resultados locales por coalición.

    """
    
    subdivrow = {0: 'Distrito', 1: 'Circunscripción'}[rep]
    datos_nac, datos_loc = [], []
    
    ## indice categórico: coaliciones seguidas de valores estadísticos
    estadistica = [x for x in listas.index.get_level_values('Lista/Pacto').drop_duplicates().tolist() if x in ['Válidamente emitidos', 'Nulos', 'Blancos', 'Blancos/Nulos','Total']]
    
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
    
    ## resultados nacionales y locales
    listas_display = listas.copy().reset_index()
    reg = []
    
    listas_display['Lista/Pacto'] = listas_display['Lista/Pacto'].map(lambda x: x if x in leyenda.keys() else (x if x in estadistica else 'Otros'))
    
    if eleccion <= 1969 and (rep == 0):
        # A falta de datos detallados, en ocasiones Santiago y Ñuble están repetidos
        if len(set(listas[(listas.index.get_level_values('Distrito').isin([''])) & (listas.index.get_level_values('Lista/Pacto').isin(estadistica[-1:]))]['Votos'].values)) == 1:
            reg.extend(['Santiago-2', 'Santiago-3', 'Santiago-4'])
        if len(set(listas[(listas.index.get_level_values('Distrito').isin(['Ñuble-1', 'Ñuble-2'])) & (listas.index.get_level_values('Lista/Pacto').isin(estadistica[-1:]))]['Votos'].values)) == 1:            
            reg.extend(['Ñuble-2'])
    
    for res in ['nacional', 'local']:
        cols = ['Lista/Pacto'] if res == 'nacional' else [subdivrow, 'Lista/Pacto']
        mask = ~listas_display[subdivrow].isin(reg) if res == 'nacional' else True
        
        coaliciones = listas_display[~listas_display[subdivrow].isin(reg)].groupby(cols).agg({'Votos': 'sum', 'Porcentaje':'sum', 'Electos': 'sum'}).reset_index()
    
        coaliciones['Lista/Pacto'] = pd.Categorical(coaliciones['Lista/Pacto'], categories=cat, ordered=True)
        coaliciones = coaliciones.sort_values(cols, ascending=[True]*len(cols)).set_index(cols)
    
        coaliciones['Votos'] = coaliciones['Votos'].astype(int)    
        if res == 'nacional':
            coaliciones['Porcentaje'] = (100*coaliciones['Votos']/coaliciones.loc[estadistica[-1]]['Votos']).round(2)    
        
        coaliciones = coaliciones.reset_index()
        coaliciones = coaliciones[coaliciones['Lista/Pacto'].notna()]
        
        mask = ~((coaliciones['Lista/Pacto'] == 'Nulos') | (coaliciones['Lista/Pacto'] == 'Blancos') | (coaliciones['Lista/Pacto'] == 'Blancos/Nulos'))
        coaliciones = coaliciones[mask]
    
        # generar tablas con resultados
        if res == 'nacional':
            datos_nac = pattern.sub(lambda m: editar[m.group(0)],
                                    coaliciones[['Lista/Pacto', 'Votos', 'Porcentaje']].to_html(justify='center', index=False, bold_rows=False, border=0, table_id='info_display')
                                    )
        else:
            for i in votacion_subdiv.index.unique():
                datos_loc.append(pattern.sub(lambda m: editar[m.group(0)], 
                                             coaliciones[coaliciones[subdivrow]==i][['Lista/Pacto', 'Votos', 'Porcentaje']].to_html(justify='center', index=False, bold_rows=False, border=0, table_id='info_display')) if i in listas.index.get_level_values(subdivrow).unique() else datos_nac
                                 )

    return datos_nac, datos_loc

#%%
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

