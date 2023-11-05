#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Sebastián RIFFO

Funciones relativas a la creación y personalización de marcadores y sus 
respectivos popups, al igual que su posterior agrupamiento a fin de facilitar
la visualización en folium.
- *marker_subdiv*: marcador personalizado en cada distrito/circunscripción.
- *popup_resultados_subdiv*: resultados electorales desplegados en una tabla ordenable.
- *markers*: agrupación de marcadores.

"""

import folium
from folium.plugins import MarkerCluster

from bs4 import BeautifulSoup

from PIL import ImageFont
font = ImageFont.truetype('/usr/share/fonts/truetype/corscore/Arimo-Regular.ttf', 12)
fonttitle = ImageFont.truetype('/usr/share/fonts/truetype/corscore/Arimo-Regular.ttf', 18)

#%%
def markers(eleccion, rep, listas, candidatos, votacion_div_electoral, fg, color_listas, leyenda):
    """
    Posicionamiento y agrupación de marcadores en folium, gracias a MarkerCluster

    Parámetros
    ----------
    eleccion : int
        Año de la elección.
    rep : int
        Elección de diputados (0) o senadores (1).
    listas : dataframe
        Info electoral por Lista/Pacto, en cada subdivisión.      
    candidatos : dataframe 
        Info electoral de candidatos en cada subdivisión. Distingue entre la 
        la lista completa de 
        - legisladores electos (columns=[Candidato, Votos, Porcentaje, url (opcional)])        
        - candidatos (columns=[Candidato, Votos, Porcentaje, Electos])
    div_electoral : geodataframe
        Geometrí­as de la division electoral, y otras informaciones, a nivel nacional.
    fg : layer
        layer vacío, que agrupará todos los marcadores
    color_listas : función
        Colormap.
    leyenda : dict[str,str]
        Nombres de listas y colores asociados, según el formato 
        {lista_1 : color_1, ... , lista_k : color_k, 'Otros' : color_o}

    Entrega
    -------
    marker_cluster : layer
        layer que contiene todos los marcadores
        
    """
    
    subdivrow = {0:'Distrito',1:'Circunscripción'}[rep]
    
    marker_cluster = MarkerCluster().add_to(fg)    
    
    for j in votacion_div_electoral.index:
        ## marcadores
        escanos_subdiv = (candidatos['Electos'].loc[j] == '*').sum() if 'Electos' in candidatos.columns else (candidatos.loc[j]['Candidatos'].notna()).sum()            
        listas_subdiv = listas.loc[j]['Electos'] if (listas is not None and j in listas.index.get_level_values(subdivrow).unique()) else candidatos.groupby(level=[0,1]).agg({'Candidatos':'count'}).loc[j]
        
        x_loc = votacion_div_electoral['marker'].y[j] 
        y_loc = votacion_div_electoral['marker'].x[j] 

        (marker_html, marker_anchor) = marker_subdiv(escanos_subdiv, listas_subdiv, color_listas)

        ## popups
        popup = popup_resultados_subdiv(eleccion, rep, escanos_subdiv, candidatos, j, leyenda) 

        ## agrupación
        folium.Marker(location= [x_loc, y_loc],
                      draggable=False,
                      popup=popup,
                      icon=folium.DivIcon(html=marker_html, icon_anchor=marker_anchor)).add_to(marker_cluster)
        
    return marker_cluster

#%%
def marker_subdiv(escanos, listas, color_listas):
    """
    Construye un marcador que representa el número total de parlamentarios en el 
    distrito/circunscripción, coloreado según los escaños obtenidos por cada coalición.
    
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

#%%
def popup_resultados_subdiv(eleccion, rep, escanos, candidatos, j, leyenda):
    """
    Código html del popup, para cada distrito o circunscripción.
    
    El popup contiene una tabla con los resultados de la elección, la cual 
    se puede ordenar mediante tablesorter (Mottie's fork). El ancho de las columnas
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
        # title = {0:('Diputados Distrito '+str(j)), 1:''.join(['Senadores ',str(j),'ª Circunscripción'])}[rep]
        title = {0:('Diputados Distrito '+str(j)[1:]), 1:''.join(['Senadores ',str(j)])}[rep]
    else:
        # if j >= 71:
        #     title = {0: 'Diputados 7ᵃ Agrupación Departamental, ', 1: 'Senadores 7ª Agrupación Senatorial, '}[rep]
        #     title += '2ᵒ Distrito' if(j % 10 == 2) else str(j % 10)+'ᵉʳ Distrito'
        # else:
            title = {0: 'Diputados ', 1: 'Senadores '}[rep] + j #str(j) + {0: 'ᵃ Agrupación Departamental ', 1: 'ª Agrupación Senatorial '}[rep]

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
