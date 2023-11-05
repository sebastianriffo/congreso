#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Sebastián RIFFO

Crea un diagrama de reparto en Highcharts, agregable a un mapa producido en folium.

"""
from modulos.pactos import siglas_partidos

import pandas as pd
import re
from unidecode import unidecode
from branca.element import Template, MacroElement

def dist_eleccion(eleccion, rep, subdivision, candidatos, leyenda, color_listas):
    """
    Diagrama con la composición de la nueva legislatura, creado en Highcharts.
    Contiene un subtí­tulo vinculado a un artí­culo de la BCN, agregado mediante
    la función *legislaturaBCN*.

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
        Colormap 

    Entrega
    -------
    macro : MacroElement
        Elemento en branca, cuyo template es el código html del diagrama antes 
        mencionado.

    """
    import math

    if 'Electos' in candidatos.columns:
        electos = candidatos[candidatos['Electos'] == '*']
        electos = electos.drop(['Electos'], axis=1)
    else:
        electos = candidatos

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
        mask = (~data_chart['Circunscripción'].isin(subdivision)) & (~data_chart['Circunscripción'].isin(['Designados']))
        data_chart.loc[mask,'Candidatos'] = '* ' + data_chart[mask]['Candidatos']
        data_chart.loc[data_chart['Circunscripción'].isin(['Designados']), 'Candidatos'] = '** ' + data_chart[data_chart['Circunscripción'].isin(['Designados'])]['Candidatos']
        
    # senadores : separar los electos (subdivision) de los ya instalados y designados 
    data_chart['Electos_total'] = 1
    data_chart['Electos_periodo'] = 1

    if rep == 1:
        data_chart.loc[(~data_chart['Circunscripción'].isin(subdivision)) | (data_chart['Circunscripción'].isin(['Designados'])), 'Electos_periodo'] = 0
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

    highcharts = f"""
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
    """

    chart_html = f"""
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

    <button id="button" class='button1' style='position: absolute; z-index:9991; left: 12px; top:12px;'></button>
    
    <div id='container'
        style='position: absolute; z-index:9990; width:{container_width}px; height:{container_height}px; left: 10px; top:10px; visibility: visible;'>    
    </div>

    <script>            
    {highcharts}
 	
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
    macro._template = Template(chart_html)
    
    apportionment_html =  f"""
    <div id='container'
        style='position: absolute; z-index:9990; width:{container_width}px; height:{container_height}px; left: 10px; top:10px; visibility: visible;'>    
    </div>

    <script>            
    {highcharts}
    </script>        
    """
    
    return macro, apportionment_html

#%%
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