#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
pd.options.mode.chained_assignment = None

from pathlib import Path
import re
from operator import itemgetter
from ast import literal_eval

from pactos import pactos_electorales, siglas_partidos

#%%    
def resultados1925_1969(candidatos, eleccion, rep, pactos, siglas, provincias):        
    """
    A partir de las listas de candidatos y pactos, se construye un dataframe
    con los resultados de partidos, entre los años 1932 y 1969. 
    Las elecciones de diputados de 1932, 1953 y 1957, e igualmente las del Senado, solo muestran 
    datos cualitativos.
        
    Parámetros
    ----------
    candidatos : dataframe 
        Info electoral por candidato, en cada subdivisión.
        indice = ['Distrito' o 'Circunscripción', 'Lista/Pacto', 'Partido']
        columnas = ['Candidatos', 'Votos', 'Porcentaje', 'Electos']  
    eleccion : int
        Año de la elección.
    rep : int
        Elección de diputados (0) o senadores (1).
    
    pactos : dict[str,str]
        Pacto electoral correspondiente a la elección. 
    siglas : dict[str,str]
        Diccionario con los nombres de partido y sus respectivas siglas.

    Entrega
    -------
    pp : dataframe o None
        Info electoral por partido político, en cada subdivisión.   
        indice = ['Distrito' o 'Circunscripción', 'Lista/Pacto', 'Partido']     
        columnas = ['Candidaturas', 'Votos', 'Porcentaje', 'Electos']

    """        
    if ((rep == 0) and eleccion in {1925,1930,1932,1937,1953,1957}) or ((rep == 1) and eleccion not in {1941}):        
        return None

    subdivrow = {0:'Distrito',1:'Circunscripción'}[rep] 
    flatten_list = lambda test:[element for item in test for element in flatten_list(item)] if type(test) is list else [test]

    pl = list(pactos.items())    
    pl.extend([('','Válidamente emitidos'),('','Blancos/Nulos'),('','Total')] if (eleccion not in {1941, 1945, 1949}) else [('','Válidamente emitidos')] )

    ## datos
    pp = votaciones1925_1969(eleccion, rep, pl, siglas)    
    pp[subdivrow] = pp['Provincias']    
    
    # estadística    
    pp.loc[pp['Lista/Pacto'] == 'Válidamente emitidos','Votos'] = pp.groupby([subdivrow], sort=False).agg({'Votos':'sum'}).values            
    
    if (eleccion not in {1941, 1945, 1949}):
        pp.loc[pp['Lista/Pacto'] == 'Total','Votos'] = pp[pp['Lista/Pacto'] == 'Total']['Total']
        pp.loc[pp['Lista/Pacto'] == 'Blancos/Nulos','Votos'] = pp[pp['Lista/Pacto'] == 'Total']['Votos'].values - pp[pp['Lista/Pacto'] == 'Válidamente emitidos']['Votos'].values

    # calcular porcentajes
    pp['Porcentaje'] = (100*pp['Votos']/pp['Total']).round(2)
    
    pp = pd.merge(pp,
                  pd.concat([candidatos[(candidatos['Lista/Pacto'] != 'Candidatura Independiente') & (candidatos['Partido'] == 'IND') 
                                        & (candidatos[subdivrow].isin(provincias)) & (candidatos['Electos'] == '*') ].groupby([subdivrow, 'Lista/Pacto']).agg({'Partido':'first', 'Electos':'count'}).reset_index(),
                            candidatos[(candidatos['Partido'] != 'IND') 
                                       & (candidatos[subdivrow].isin(provincias)) & (candidatos['Electos'] == '*')].groupby([subdivrow, 'Partido']).agg({'Lista/Pacto':'first', 'Electos':'count'}).reset_index(),
                            candidatos[(candidatos['Lista/Pacto'] == 'Candidatura Independiente') 
                                       & (candidatos[subdivrow].isin(provincias)) & (candidatos['Electos'] == '*')]
                            ])[[subdivrow,'Partido','Electos']],
                   how="outer")#.fillna(0)
    pp = pp[pp['Provincias'].notna()].fillna(0)
        
    pp['Electos'] = pp['Electos'].map(lambda x: 1 if x == '*'else x).astype(int)        

    # pp[subdivrow] = pd.Categorical(pp[subdivrow], categories=provincias, ordered=False)
    pp[subdivrow] = pd.Categorical(pp[subdivrow], categories=pp['Circunscripción'].unique().tolist(), ordered=False)    
    return pp[[subdivrow, 'Lista/Pacto', 'Partido', 'Electos', 'Porcentaje', 'Votos']]


#%%
def votaciones1925_1969(eleccion, rep, pl, siglas):
    """
    Fuentes : 
    - Urzua Valenzuela
    - Aldunate
    - https://pdba.georgetown.edu/Elecdata/Chile/cong_totals.html
    - Moroni
    - Ibáñez    

    Parameters
    ----------
    eleccion : TYPE
        DESCRIPTION.
    rep : TYPE
        DESCRIPTION.
    provincias : TYPE
        DESCRIPTION.
    pl : TYPE
        DESCRIPTION.
    siglas : TYPE
        DESCRIPTION.

    Returns
    -------
    pp : TYPE
        DESCRIPTION.
    agg : TYPE
        DESCRIPTION.

    """    
    if eleccion < 1937:
        Exception()

    flatten_list = lambda test:[element for item in test for element in flatten_list(item)] if type(test) is list else [test]
    
    if rep == 0:
        provincias = flatten_list(['Tarapacá', 'Antofagasta', 'Atacama', 'Coquimbo', 'Aconcagua', 'Valparaíso', 
                                   ['Santiago-1', 'Santiago-2', 'Santiago-3', 'Santiago-4'], "O'Higgins", 'Colchagua', 'Curicó', 'Talca', 'Maule', 'Linares',
                                   ['Ñuble-1', 'Ñuble-2'], 'Concepción', 'Arauco', 'Bío-Bío', 'Malleco', 'Cautín', 
                                   ['Valdivia', 'Osorno', 'Llanquihue', 'Chiloé', 'Aysén'] if eleccion >= 1941 else ['Valdivia', 'Llanquihue y Aysén', 'Chiloé'], 
                                   'Magallanes'])    
    else:
        circ = flatten_list(['Tarapacá y Antofagasta', 'Atacama y Coquimbo', 'Aconcagua y Valparaíso', 'Santiago', 
                             "O'Higgins y Colchagua", 'Curicó, Talca, Maule y Linares', 'Ñuble, Concepción y Arauco', 'Bío-Bío, Malleco y Cautín',
                             'Valdivia, Llanquihue, Chiloé, Aysén y Magallanes' if eleccion <= 1937 else (('Valdivia, Osorno, Llanquihue, Chiloé, Aysén y Magallanes') if eleccion < 1969 else ['Valdivia, Osorno y Llanquihue', 'Chiloé, Aysén y Magallanes']) 
                             ])
        r = list(filter(re.compile('Tarapacá|Aconcagua|Colchagua|Concepción|Valdivia|Chiloé').findall, circ))
        
        provincias = r if ((eleccion-1937)%8 == 0) else [x for x in circ if x not in r]

    agg = [0,0]    
            
    if eleccion == 1969:        
        # TOTALES DIPUTADOS (Aldunate, p.227), SENADORES (Urzúa Valenzuela, p.620).
        # santiago : 917937= I+II+337900+IV (Ibáñez).
        # ñuble: 72893 = 21758+51115 (Ibáñez).
        pp = pd.merge(pd.DataFrame.from_records([(d,l,p) for d in provincias for p,l in pl], columns = ['Provincias', 'Lista/Pacto', 'Partido'] ),
                      pd.DataFrame({'Total': flatten_list([51915, 78262, 38564, 80236, 48296, 270671, [917937]*4, 85236, 43323, 29395, 52635, 23195, 44915,
                                                          [21758,51115], 167678, 21141, 39379, 41141, 89498, 62265, 40695, 39070, 25801, 11322, 30686]) if (rep == 0) else [124795, 304059, 123326, 252047, 136547, 65275],
                                   'Provincias': provincias}),
                      how="outer")

        # DETALLE DIPUTADOS (Urzúa Valenzuela, p.621).
        # PC : hay un error (asumo que un typo en Santiago-1, 42536 en vez de 42356 (confirmar)), que deja el total en -180 vs el valor de Nohlen.
        # PR : typo en Cautín, 9235 en vez de 9325 (Ibáñez).
        # PS : 7500 en Colchagua (Ibáñez).
        # IND : Va en Santiago, pero cual distrito ? (no el tercero).
        agg = [1,0]
                      
        pp.loc[pp['Partido'] == siglas['Partido Comunista'],'Votos'] = flatten_list([16563, 18121, 7991, 13331, 6221, 60373, [42536,39256,58519,13035], 10558, 2289, 3496, 8765, 0, 2525,
                                                                                   [591,4707], 43725, 4948, 7748, 2556, 6894, 2729, 0, 0, 0, 2390, 3182]) if (rep == 0) else [43709, 67971, 16338, 53470, 0, 0]
        pp.loc[pp['Partido'] == siglas['Partido Demócrata Cristiano'],'Votos'] = flatten_list([13985, 20814, 10103, 20418, 13730, 87389, [93326,63648,94605,29464], 22891, 11840, 9175, 15617, 5692, 14591,
                                                                                             [7264,13229], 49834, 5198, 10629, 12706, 31684, 16929, 9873, 11264, 6690, 3675, 10284]) if (rep == 0) else [39024, 112756, 37854, 91471, 42073, 22070]
        pp.loc[pp['Partido'] == siglas['Partido Nacional'],'Votos'] = flatten_list([9231, 6350, 2646, 10635, 11264, 49610, [70814,29563,88424,20994], 18930, 10020, 4745, 10627, 5683, 8348,
                                                                                  [5487,8915], 18478, 0, 8761, 9957, 28986, 13499, 6961, 10162, 8048, 2228, 1157]) if (rep == 0) else [10027, 57324, 26950, 34463, 31073, 13459]
        pp.loc[pp['Partido'] == siglas['Partido Radical'],'Votos'] = flatten_list([5677, 17193, 8482, 16019, 6332, 32845, [32449,13631,20678,6503], 7831, 8708, 5581, 9656, 4981, 9045,
                                                                                 [4706,15258], 23293, 5048, 6218, 11175, 9235, 6816, 11382, 4488, 6136, 904, 3289]) if (rep == 0) else [13306, 50104, 19105, 40520, 27877, 9963]
        pp.loc[pp['Partido'] == siglas['Partido Socialista'],'Votos'] = flatten_list([2035, 4138, 7625, 14628, 4263, 21952, [29161,33079,54057,10531], 12966, 7500, 4071, 0, 0, 3176,
                                                                                    [2898,6570], 19450, 2379, 3926, 1388, 0, 17319, 9748, 7616, 3546, 0, 10426]) if (rep == 0) else [4850, 13289, 21717, 30463, 32654, 17656]
        pp.loc[pp['Partido'] == siglas['Unión Socialista Popular'],'Votos'] = flatten_list([2071, 6885, 270, 2155, 3399, 1139, [2349,3067,1657,1309], 3980, 643, 1151, 0, 0, 5943,
                                                                                          [0]*2, 1854, 2529, 0, 2018, 1167, 1192, 587, 3731, 317, 1567, 924]) if (rep == 0) else [13879, 2615, 1362, 1660, 2870, 2037]
        if (rep == 0):
            pp.loc[pp['Partido'] == siglas['Partido Social Demócrata'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 945, [1780,0,0,4223], 3097, 0, 0, 895, 3606, 0,
                                                                                              [0]*2, 1263, 0, 0, 0, 4751, 0, 0, 0, 0, 0, 0])
            pp.loc[pp['Partido'] == siglas['Partido Democrático Nacional'],'Votos'] = flatten_list([458, 1725, 223, 793, 590, 3735, [5210,2868,3758,643], 980, 763, 455, 5996, 2842, 192,
                                                                                                  [86,354], 3731, 182, 1053, 460, 4990, 1219, 477, 455, 79, 105, 396]) 
            pp.loc[pp['Partido'] == siglas['Candidatura Independiente'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [2104,0,0,0], 0, 0, 0, 0, 0, 0,
                                                                                   [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    if eleccion == 1965:        
        # TOTALES DIPUTADOS (Aldunate, p.217 y 221).
        # ñuble : estimación de totales (20290,20291) en base a Moroni. 
        pp = pd.merge(pd.DataFrame.from_records([(d,l,p) for d in provincias for p,l in pl], columns = ['Provincias', 'Lista/Pacto', 'Partido'] ),
                      pd.DataFrame({'Total_v': flatten_list([26173, 42610, 22731, 42413, 24156, 125585, [458512]*4, 43171, 21972, 15109, 27392, 11683, 23364, 
                                                            [38184]*2, 85492, 12366, 23417, 24367, 54057, 36533, 22516, 23555, 11726, 5381, 15779]),
                                    'Total_m': flatten_list([21857, 32891, 16199, 35473, 20938, 133119, [479338]*4, 36495, 18115, 13137, 24104, 10456, 19706,
                                                            [29836]*2, 72839, 7338, 13636, 16962, 33387, 24513, 14760, 14313, 10148, 2843, 12476]),                                   
                                    'Provincias': provincias}),
                      how="outer")        
        pp['Total'] = pp['Total_v'] +pp['Total_m']        
        
        pp.loc[pp['Provincias'] == 'Nuble-1', 'Total'] = 20290
        pp.loc[pp['Provincias'] == 'Nuble-2', 'Total'] = 47730
        
        # DETALLE DIPUTADOS (Urzúa Valenzuela, p.610). 
        # Hay inconsistencias en el orden (contraste con Moroni y Aldunate) y datos faltantes (obtenidos de pdba).        
        # PC : votación de Cautín va en Valdivia. Falta Coquimbo (13077+159) para ajustar el total y el valor porcentual de Aldunate.
        # PR : Falta Coquimbo (14565-100), para ajustar el total y el valor porcentual de Aldunate.
        # PS : Cautín, Valdivia y Osorno van uno más abajo.
        # PADENA : los datos de Linares, Ñuble y Concepción están corridos. De PDBA sale Santiago 1-2-3 (9104), pero agrupado. -2 al total según Nohlen
        # DAL : los datos originales están corridos. Discrepancia en Atacama (según Moroni) o Coquimbo (PDBA/Urzua). +2 al total según Nohlen.
        # PDo : datos corridos. Falta Coquimbo (139, según Aldunate/PDBA), Moroni en cambio señala Atacama.
        # AN : Tarapacá va en Antofagasta.
        # CP : dato corrido, va en Linares en vez de Arauco.
        # VNP : 9,10,12 están bien posicionados. Los otros 2 están corridos, linares en vez de concepción, cautín en vez de chiloé. 
        #       Falta Valparaíso (1320) y Santiago 1-2-3 (1913-152). 
        # DC : falta la votacion de aysen (3072)
        # PL : en Colchagua hay discrepancia con Moroni (4.75), más no con Aldunate (11.17). El dato coincide con PDBA y el total de Wikipedia.        
        # IND : al cambiar valparaíso (1244+80) se ajusta la discrepancia porcentual con Moroni/Aldunate (0.48 vs 0.51)
               
        agg = [1,0]  
        
        pp.loc[pp['Partido'] == siglas['Acción Nacional'],'Votos'] = flatten_list([0, 217, 0, 0, 0, 1564, [5102,2230,5041,824], 0, 0, 0, 195, 0, 0,
                                                                                 [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        pp.loc[pp['Partido'] == siglas['Comandos Populares'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [1438,0,1353,0], 0, 0, 0, 0, 0, 330,
                                                                                    [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])        
        pp.loc[pp['Partido'] == siglas['Partido Comunista'],'Votos'] = flatten_list([17979, 16073, 6612, 13236, 0, 35429, [39869,28409,45763,12408], 12574, 0, 0, 0, 0, 0,
                                                                                   [0,5008], 38641, 4190, 6675, 0, 0, 4378, 0, 0, 3391, 0, 0])        
        pp.loc[pp['Partido'] == siglas['Partido Conservador Unido'],'Votos'] = flatten_list([0, 0, 0, 0, 3003, 13800, [17706,9877,14336,9436], 7416, 4371, 564, 5860, 538, 4353,
                                                                                           [0,5056], 3434, 0, 2120, 1183, 7685, 0, 0, 5806, 4805, 533, 0])    
        pp.loc[pp['Partido'] == siglas['Democracia Agrario Laborista'],'Votos'] = flatten_list([0, 0, 0, 230, 0, 742, [4597,3500,4248,0], 0, 0, 0, 0, 0, 73,
                                                                                              [0,515], 414, 0, 854, 1303, 3515, 2563, 0, 0, 0, 0, 0])                    
        pp.loc[pp['Partido'] == siglas['Partido Demócrata Cristiano'],'Votos'] = flatten_list([15013, 25436, 15626, 24550, 19664, 133014, [158337,93037,151824,40358], 31585, 17399, 12083, 19265, 7208, 17164,
                                                                                             [9439,20825], 61670, 4422, 12880, 12697, 32528, 22598, 15199, 13829, 4465, 3072, 0])
        pp.loc[pp['Partido'] == siglas['Partido Democrático'],'Votos'] = flatten_list([73, 88, 0, 139, 0, 2941, [4192,4049,4977,801], 0, 44, 147, 131, 0, 193,
                                                                                     [0, 125], 395, 0, 1106, 479, 717, 921, 0, 0, 0, 0, 0])        
        pp.loc[pp['Partido'] == siglas['Partido Democrático Nacional'],'Votos'] = flatten_list([0, 3300, 0, 0, 0, 0, [9104,0,0,6417], 6905, 0, 0, 11599, 4526, 2354,
                                                                                              [0,3427], 8745, 0, 0, 0, 18206, 0, 0, 0, 0, 0, 0])
        pp.loc[pp['Partido'] == siglas['Partido Liberal'],'Votos'] = flatten_list([6732, 4829, 0, 9096, 5553, 19770, [12842,6936,26297,4444], 3785, 4479, 3016, 4639, 4727, 2432,
                                                                                 [2820,126], 5998, 0, 3306, 11712, 9235, 6309, 2331, 7024, 2877, 664, 0])
        pp.loc[pp['Partido'] == siglas['Partido Radical'],'Votos'] = flatten_list([7409, 12606, 7935, 14465, 4433, 24420, [37139,13617,25606,9579], 4673, 4907, 4731, 7234, 4561, 7265,
                                                                                 [4694,12030], 24174, 5873, 8804, 8222, 12677, 11042, 10958, 3876, 5889, 1407, 12686])
        pp.loc[pp['Partido'] == siglas['Partido Socialista'],'Votos'] = flatten_list([0, 11688, 7424, 13897, 11904, 15656, [19508,24369,40526,0], 9859, 7997, 6677, 0, 0, 7182,
                                                                                    [2916,0], 12239, 5083, 0, 4819, 0, 11978, 3862, 6695, 0, 2339, 14975])
        pp.loc[pp['Partido'] == siglas['Vanguardia Nacional del Pueblo'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 1320, [1913,0,0,195], 541, 57, 0, 970, 0, 430,
                                                                                                [0]*2, 0, 0, 0, 0, 406, 0, 0, 0, 0, 0, 0])        
        pp.loc[pp['Partido'] == siglas['Candidatura Independiente'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 1324, [0]*4, 0, 0, 0, 0, 0, 0,
                                                                               [0]*2, 0, 0, 0, 0, 0, 0, 4345, 0, 0, 0, 0])

    if eleccion == 1961:
        # TOTALES DIPUTADOS (Aldunate p.213; p.215 y 219 totales varones y mujeres)       
        # En Coquimbo y Curicó se usa la suma entre varones y mujeres, diff de +10 y +20, que cuadra los votos totales.
        # Aysén y Chiloé están intercambiados. 
        pp = pd.merge(pd.DataFrame.from_records([(d,l,p) for d in provincias for p,l in pl], columns = ['Provincias', 'Lista/Pacto', 'Partido'] ),
                      pd.DataFrame({'Total': flatten_list([25293, 48198, 25446, 52967, 31280, 141396, [440477]*4, 57904, 33436, 20557, 37213, 18370, 32104,
                                                          [52015]*2, 101931, 16321, 25389, 31706, 59413, 41905, 24835, 25660, 17720, 4953, 19187]),
                                   'Provincias': provincias}),
                      how="outer")
        
        # DETALLE DIPUTADOS (Urzúa Valenzuela, p.598).
        # PADENA : typo en Valparaíso (18673 en vez de 673).
        # CP, UNL, IND : obtenidos de PDBA.
        # PC : Valdivia, se usa pdba (4371 vs 3371), coincide el total.
        # PCU : posible typo en Antofagasta, se usa pdba (2704 vs 3704), que hace coincidir el total.
        agg = [1,0]        
        
        pp.loc[pp['Partido'] == siglas['Comandos Populares'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [0]*4, 0, 0, 0, 0, 0, 0,
                                                                                    [0]*2, 0, 0, 0, 0, 96, 0, 0, 0, 0, 0, 0])
        pp.loc[pp['Partido'] == siglas['Partido Comunista'],'Votos'] = flatten_list([6022, 9993, 5711, 7574, 0, 15366, [23365,15946,19731,7263], 9370, 0, 0, 4144, 0, 0,
                                                                                   [655]*2, 16296, 3781, 3085, 0, 2240, 4371, 0, 1979, 0, 680, 0])  
        pp.loc[pp['Partido'] == siglas['Partido Conservador Unido'],'Votos'] = flatten_list([0, 2704, 0, 3456, 4582, 23146, [32532,15554,19316,10833], 10267, 10200, 3576, 8904, 1621, 5730,
                                                                                           [6129]*2, 14740, 0, 2773, 3167, 7179, 926, 0, 5915, 3991, 874, 145])  
        pp.loc[pp['Partido'] == siglas['Partido Democrático'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [395,74,0,0], 0, 0, 0, 0, 0, 0,
                                                                                     [137]*2, 0, 166, 0, 0, 0, 0, 0, 0, 0, 0, 0])  
        pp.loc[pp['Partido'] == siglas['Partido Demócrata Cristiano'],'Votos'] = flatten_list([3767, 6402, 5346, 5292, 4917, 22404, [30780,14244,20434,7742], 7478, 6229, 4188, 3853, 5293, 5760,
                                                                                             [13145]*2, 14536, 1895, 4161, 4733, 5011, 6483, 4721, 2723, 991, 397, 543])
        pp.loc[pp['Partido'] == siglas['Partido Democrático Nacional'],'Votos'] = flatten_list([48, 48, 0, 0, 0, 18673, [12060,1286,0,8521], 6915, 0, 0, 9607, 4226, 0,
                                                                                              [3458]*2, 8149, 114, 0, 1634, 17184, 3119, 137, 0, 0, 0, 0])  
        pp.loc[pp['Partido'] == siglas['Partido Liberal'],'Votos'] = flatten_list([5783, 6044, 5377, 13436, 7513, 15798, [20840,10855,31605,8521], 6884, 5126, 3265, 4517, 4138, 5904,
                                                                                 [7741]*2, 7247, 0, 4096, 12571, 9773, 9079, 7294, 4665, 3124, 758, 531])  
        pp.loc[pp['Partido'] == siglas['Partido Radical'],'Votos'] = flatten_list([6936, 13178, 8624, 14875, 6157, 24680, [37676,15762,19241,5768], 8132, 5864, 4528, 5058, 2912, 7854,
                                                                                 [16311]*2, 25649, 3463, 7190, 6015, 10850, 10983, 6839, 6682, 5731, 1254, 8616])
        pp.loc[pp['Partido'] == siglas['Partido Socialista'],'Votos'] = flatten_list([1851, 8030, 0, 7376, 6709, 13252, [13104,5621,17641,0], 6726, 4881, 4610, 0, 0, 5990,
                                                                                    [2634]*2, 11226, 3673, 3038, 2777, 5304, 5033, 4940, 2486, 2982, 699, 8539])   
        pp.loc[pp['Partido'] == siglas['Unión Nacional Laborista'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 3255, [0]*4, 0, 0, 0, 102, 0, 37,
                                                                                          [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])   
        pp.loc[pp['Partido'] == siglas['Candidatura Independiente'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [0]*4, 0, 0, 0, 0, 0, 0,
                                                                               [0]*2, 0, 0, 0, 2720, 0, 0, 0, 0, 0, 0, 0])                      

    if eleccion == 1957:        
        # TOTALES DIPUTADOS (Aldunate, p.211). 
        # Colchagua : 37948 en vez de 22948 (coincide con totales de Nohlen y porcentajes de Aldunate).
        pp = pd.merge(pd.DataFrame.from_records([(d,l,p) for d in provincias for p,l in pl], columns = ['Provincias', 'Lista/Pacto', 'Partido'] ),
                      pd.DataFrame({'Total': flatten_list([14817, 18305, 13068, 33079, 23440, 83389, [256853]*4, 34969, 22948, 14805, 29175, 14980, 27661,
                                                          [38770]*2, 60236, 9306, 19725, 24889, 46345, 30404, 17719, 17838, 12646, 2901, 9961]),
                                    'Provincias': provincias}),
                      how="outer")
        
        # DETALLE DIPUTADOS (Urzúa Valenzuela, p.579; los datos faltantes se obtuvieron de pdba)
        # Partido del Trabajo (comunista) : Antofagasta (359 en vez de 353, de modo que cuadre la región) . Total : 17784 vs 17785 = -1
        # MR: typo en Antogasta (1806 es 1086), valparaíso (2957 en vez de 2950, coincide con pdba, compensa total partido y total provincial)
        # PN («democrático nacional»): El valor de Santiago parece ser solo el primer distrito, 4437 (en vez de 3444) hace coincidir el total nacional (Nohlen).                 
        # PDo : typo en Santiago-1 (11583 es 1583)
        # FN : typo en Talca (2586 en vez de 2486), que coincide con el porcentaje de Aldunate, compensa el total partido y provincial.
        # PRDo : falta Antofagasta (1)
        # MONAP : total de 1342 según Nohlen, pero Urzúa Valenzuela incluye Santiago 2-3 :602 y 188.
        # PR : 188527 vs 188526 = +1 (sobra 1 en santiago)
        
        # socialistas : PS y PSP vienen agregados.            
        # PSP : Tarapacá (1685 en vez de 1691, de modo que cuadre la región), cautin = 2519+77, que cuadra la región y la suma socialista de Urzua.
        # PS : nuble=2036+52, que cuadran la región y la suma socialista de Urzua.
        # Santiago está agregado, la suma de PDBA (27420=16314+10926) difiere en 181 de Urzua-Valenzuela (27239=9617+5236+10051+2335).        

        # democráticos : al parecer Urzúa agrega ambos democráticos en Nuble, Malleco y Cautín
        # PDo : 44509 vs 44213 = +296
        # PDD : 3006 vs 3302 = -296 (PDBA incluye votos en Nuble, malleco y cautín : 26,137,145=308)
        
        # conservadores : PCU (unido, ex-tradicionalista) y conservador (socialcristiano), vienen agregados      
        # en Santiago-3 y -4 solo hubo candidaturas PCU 
        # Comparacion con Nohlen desagregando por PDBA
        # PCU : 124119 vs 121223 = +2896
        # PCSC : 30506 vs 33654 = -3148        
        # esta diferencia se explica minimamente por la discrepancia de sumas en Valpo (16499 vs 16529 = -30), colchagua (10057 vs 10053 = +4), nuble (6095 vs 6338 = -243), malleco (1181 (167+1014) vs 1164 = +17). 
        # No es claro a quién agregarle estos valores (30-4+243-17 = 252). 
        # la hipótesis es que hay uno o más valores cambiados. Verificamos y descartamos las provincias con uno o ningún competidor
        # 1-Tarapacá, 2-Antofagasta, 3-Atacama, 18-Arauco, 21-Cautin, 22-valdivia
        # 23-osorno, 24-llanquihue, 25-castro, 26-magallanes (la candidata maría elena vukovic aparece como conservadora)
        # 
        # y aquellas en que uno de los partidos (mas no ambos) resultó electo : 
        # 4-Coquimbo, 5-aconcagua, 6-valpo,8-santiago,9-ohiggins,10-colchagua,12-talca,19-biobio        
        # quedan
        # 11-curico, 2626 (en 53 ganaron la diputacion, pcsc no se presentó)
        # 13-maule, -1375 (acá casi ganó el PCSC)
        # 14-linares, 1610 (linares PCU; 2232, pSCS 0)
        # 15-nuble, 1913 (53: PCU 4012 / PCSC 1941)
        # 17-conce, 4818 (53: PCU 4034/ PCSC 3050)
        # 20-malleco, 847 (53:PCU no compitio, PCSC saco 474)        
        agg = [1,0]
                
        pp.loc[pp['Partido'] == siglas['Partido Agrario Laborista'],'Votos'] = flatten_list([235, 1313, 0, 1192, 3455, 1368, [7863,1713,8158,4528], 3719, 2012, 762, 3853, 1437, 3389,
                                                                                           [6756]*2, 1248, 0, 0, 3080, 4029, 1904, 644, 5248, 0, 696, 0])             
        pp.loc[pp['Partido'] == siglas['Partido Conservador Social Cristiano'],'Votos'] = flatten_list([0, 0, 0, 17, 3017, 3004, [7888,0,0,0], 111, 2085, 376, 1800, 2502, 1677,
                                                                                                      [2091]*2, 4073, 0, 594, 167, 0, 1104, 0, 0, 0, 0, 0])           
        pp.loc[pp['Partido'] == siglas['Partido Conservador Unido'],'Votos'] = flatten_list([0, 246, 0, 4239, 4625, 13495, [19637,0,8690,6893], 9684, 7972, 3002, 4203, 1145, 3287,
                                                                                            [4004]*2, 8891, 2624, 4076, 1014, 4128, 0, 1685, 4409, 3704, 437, 2029])
        pp.loc[pp['Partido'] == siglas['Partido Democrático'],'Votos'] = flatten_list([0, 805, 331, 0, 465, 8949, [1583,13,3436,2789], 3063, 150, 1, 953, 3708, 1860,
                                                                                     [1052]*2, 3721, 0, 198, 2582, 5040, 3368, 442, 0, 0, 0, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido Democrático Doctrinario'],'Votos'] = flatten_list([0, 33, 0, 0, 0, 0, [2575,185,213,0], 0, 0, 0, 0, 0, 0,
                                                                                                 [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])         
        pp.loc[pp['Partido'] == siglas['Falange Nacional'],'Votos'] = flatten_list([1990, 2881, 3050, 1923, 1162, 4466, [16004,6099,11849,5032], 3104, 0, 0, 2486, 0, 2724,
                                                                                  [1897]*2, 4611, 0, 0, 0, 6994, 2038, 1294, 2058, 463, 585, 0])  
        pp.loc[pp['Partido'] == siglas['Partido Laborista'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [1873,3650,0,0], 0, 0, 32, 0, 0, 0,
                                                                                   [0]*2, 2455, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])  
        pp.loc[pp['Partido'] == siglas['Partido Liberal'],'Votos'] = flatten_list([2467, 2205, 3345, 9392, 6020, 8368, [13643,1414,11511,4166], 6780, 6071, 3019, 5439, 3396, 6961,
                                                                                 [5823]*2, 4276, 0, 2977, 7621, 4103, 8749, 3098, 1785, 1821, 291, 0])  
        pp.loc[pp['Partido'] == siglas['Movimiento Nacional del Pueblo'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [1342,0,0,0], 0, 0, 0, 0, 0, 0, 
                                                                                                [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])  
        pp.loc[pp['Partido'] == siglas['Movimiento Republicano'],'Votos'] = flatten_list([1789, 1086, 0, 0, 0, 2957, [2001,0,802,0], 0, 0, 0, 0, 0, 0,
                                                                                        [0]*2, 0, 0, 0, 0, 0, 0, 1758, 0, 0, 0, 0])          
        pp.loc[pp['Partido'] == siglas['Partido Nacional'],'Votos'] = flatten_list([0, 0, 0, 1358, 0, 5755, [4437,0,0,0], 12, 0, 2786, 2012, 0, 3642,
                                                                                  [0]*2, 2087, 19, 2594, 3701, 5394, 1730, 622, 158, 1626, 42, 0])
        pp.loc[pp['Partido'] == siglas['Partido Nacional Cristiano'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [1026,3965,0,0], 0, 423, 0, 0, 0, 0,
                                                                                            [0]*2, 0, 0, 0, 0, 3671, 0, 0, 0, 0, 0, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido del Trabajo'],'Votos'] = flatten_list([2, 359, 0, 1577, 0, 0, [3798,2795,0,2914], 2861, 0, 0, 158, 592, 0,
                                                                                     [0]*2, 0, 0, 248, 0, 0, 2385, 0, 0, 95, 0, 0])        
        pp.loc[pp['Partido'] == siglas['Partido Radical'],'Votos'] = flatten_list([4399, 6559, 3851, 10608, 4294, 16862, [24880,6778,11320,3427], 3666, 3147, 3039, 5984, 1881, 3245,
                                                                                 [14296]*2, 14013, 4265, 6371, 4984, 8696, 6883, 5685, 4179, 3442, 850, 923])        
        pp.loc[pp['Partido'] == siglas['Partido Radical Doctrinario'],'Votos'] = flatten_list([411, 1, 0, 0, 0, 0, [3476,0,0,0], 0, 0, 0, 0, 0, 0,
                                                                                             0, 0, 0, 0, 0, 0, 1689, 0, 0, 0, 0, 0, 0])
        pp.loc[pp['Partido'] == siglas['Partido Socialista'],'Votos'] = flatten_list([1839, 0, 0, 552, 0, 7001, [16314,0,0,0], 1969, 0, 167, 595, 0, 0,
                                                                                    [2088]*2, 8133, 0, 0, 0, 5, 7, 112, 1, 0, 0, 0])
        pp.loc[pp['Partido'] == siglas['Partido Socialista Popular'],'Votos'] = flatten_list([1685, 2817, 2491, 2221, 402, 1691, [10926,0,0,0], 0, 1092, 1621, 1692, 319, 876,
                                                                                            [520]*2, 6728, 2398, 2667, 1757, 2596, 2236, 2379, 0, 1495, 0, 4396])  
        pp.loc[pp['Partido'] == siglas['Candidatura Independiente'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 9443, [5248,0,0,0], 0, 0, 0, 0, 0, 0,
                                                                               [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2613]) 
           
    if eleccion == 1953:           
        # TOTALES DIPUTADOS (Aldunate, p.194)  
        # Chiloé y Aysén están invertidos
        pp = pd.merge(pd.DataFrame.from_records([(d,l,p) for d in provincias for p,l in pl], columns = ['Provincias', 'Lista/Pacto', 'Partido'] ),
                      pd.DataFrame({'Total': flatten_list([12884, 19346, 10437, 28380, 20302, 75165, [234607]*4, 32406, 20756, 12451, 25693, 14030, 24648,
                                                          [34062]*2, 52485, 8502, 16936, 20934, 41006, 26925, 15903, 15753, 11084, 2325, 9791]),
                                    'Provincias': provincias}),
                      how="outer")
        
        # DETALLE DIPUTADOS (Urzúa Valenzuela, p.550)        
        # Conservador (socialcristiano) 
        # Democrático (de chile)
        # MNI : discrepancia en Llanquihue-Aysén, 477+16 vs 516, -23 vs total de Nohlen.
        agg = [1,1] 
        
        pp.loc[pp['Partido'] == siglas['Acción Renovadora de Chile'],'Votos'] = flatten_list([0, 0, 0, 0, 13, 3094, [6222,151,0,0], 0, 0, 0, 0, 0, 0,
                                                                                            [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido Agrario'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [143,1,0,0], 0, 0, 336, 1, 0, 2792,
                                                                                 [330,0], 0, 0, 425, 1704, 2393, 0, 0, 0, 0, 0, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido Agrario Laborista'],'Votos'] = flatten_list([663, 1191, 0, 1195, 3403, 8415, [13944,6727,9958,3515], 4303, 1977, 2309, 10159, 3511, 7778,
                                                                                           [2829,1798], 4741, 0, 2596, 3235, 8942, 5798, 3209, 4935, 534, 818, 0])         
        pp.loc[pp['Partido'] == siglas['Partido Conservador Social Cristiano'],'Votos'] = flatten_list([0, 251, 0, 1197, 1699, 7167, [2366,0,3080,0], 621, 840, 0, 1779, 1679, 0,
                                                                                                      [912,1029], 3050, 780, 0, 474, 412, 1447, 1552, 2271, 233, 308, 185])         
        pp.loc[pp['Partido'] == siglas['Partido Conservador Tradicionalista'],'Votos'] = flatten_list([0, 376, 0, 59, 2458, 5156, [8928,5805,5300,6458], 6881, 8151, 1754, 5135, 73, 2232,
                                                                                                     [1167,2845], 4034, 1504, 1803, 0, 3385, 0, 77, 2483, 2297, 22, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido Democrático'],'Votos'] = flatten_list([0, 406, 0, 0, 13, 1129, [0,0,305,724], 0, 0, 0, 0, 0, 0,
                                                                                     [0,1181], 2789, 12, 2238, 1006, 73, 1620, 0, 71, 0, 3, 0])         
        pp.loc[pp['Partido'] == siglas['Partido Democrático del Pueblo'],'Votos'] = flatten_list([119, 259, 0, 265, 0, 1694, [7257,727,1081,2935], 0, 0, 414, 0, 4242, 0,
                                                                                                [0,1343], 5302, 1444, 665, 55, 471, 2737, 344, 190, 174, 243, 0]) 
        pp.loc[pp['Partido'] == siglas['Falange Nacional'],'Votos'] = flatten_list([1906, 2003, 2009, 1130, 0, 942, [2247,1344,0,3260], 2244, 0, 38, 618, 232, 310,
                                                                                  [0]*2, 11, 0, 399, 0, 1067, 1811, 25, 0, 757, 0, 0])         
        pp.loc[pp['Partido'] == siglas['Partido Laborista'],'Votos'] = flatten_list([0, 114, 0, 0, 0, 582, [1593,4001,0,0], 0, 0, 0, 0, 0, 0,
                                                                                   [0]*2, 1376, 0, 0, 0, 0, 505, 0, 0, 0, 0, 0])         
        pp.loc[pp['Partido'] == siglas['Partido Liberal'],'Votos'] = flatten_list([1949, 1903, 0, 8711, 3636, 6296, [4564,2458,6051,1093], 3963, 3647, 2741, 2757, 3276, 3569,
                                                                                 [2496,1939], 4858, 0, 1287, 5376, 2684, 4841, 3633, 462, 734, 0, 0])        
        pp.loc[pp['Partido'] == siglas['Movimiento Nacional del Pueblo'],'Votos'] = flatten_list([60, 594, 0, 876, 0, 0, [8468,982,3490,0], 42, 265, 0, 0, 0, 0,
                                                                                                [3,353], 2167, 0, 0, 0, 263, 306, 395, 0, 0, 0, 974]) 
        pp.loc[pp['Partido'] == siglas['Movimiento Nacional Ibañista'],'Votos'] = flatten_list([493, 985, 25, 268, 2182, 13108, [468,406,1082,2934], 1271, 0, 0, 0, 0, 0,
                                                                                              [82,1900], 321, 25, 0, 4, 1101, 1768, 36, 477, 1, 16, 0])         
        pp.loc[pp['Partido'] == siglas['Partido Nacional Cristiano'],'Votos'] = flatten_list([0, 151, 0, 243, 0, 489, [4176,5166,1515,13], 0, 1748, 0, 450, 0, 1393,
                                                                                            [55,776], 168, 0, 0, 480, 4393, 133, 0, 0, 32, 0, 0])         
        pp.loc[pp['Partido'] == siglas['Partido Radical'],'Votos'] = flatten_list([2605, 3391, 3595, 6819, 2938, 9024, [9198,3181,5096,2920], 2571, 1126, 1913, 2167, 497, 3176,
                                                                                 [2144,4998], 7504, 891, 3864, 3244, 6345, 2788, 2485, 3009, 3021, 597, 2543])        
        pp.loc[pp['Partido'] == siglas['Partido Radical Doctrinario'],'Votos'] = flatten_list([101, 275, 0, 148, 440, 1509, [3681,374,5182,175], 0, 0, 0, 388, 0, 0,
                                                                                             [0,639], 0, 0, 1465, 1572, 1325, 608, 0, 0, 0, 0, 0])         
        pp.loc[pp['Partido'] == siglas['Partido Socialista'],'Votos'] = flatten_list([2641, 2080, 0, 1464, 610, 3864, [9229,6142,3595,772], 1473, 758, 187, 576, 0, 114,
                                                                                    [78,1420], 4561, 698, 248, 0, 0, 608, 234, 129, 55, 54, 89])
        pp.loc[pp['Partido'] == siglas['Partido Socialista Popular'],'Votos'] = flatten_list([1312, 3636, 2260, 4071, 1508, 4456, [4485,1863,6064,2010], 821, 995, 2728, 1127, 513, 2453,
                                                                                            [1272,1392], 8091, 772, 1860, 2745, 2080, 1042, 1642, 788, 2172, 215, 3845]) 
        pp.loc[pp['Partido'] == siglas['Unión Nacional de Independientes'],'Votos'] = flatten_list([410, 659, 2443, 1728, 1266, 1424, [6091,1579,5238,733], 7848, 1162, 0, 0, 0, 0,
                                                                                                  [2,0], 3088, 443, 0, 26, 3540, 17, 2074, 8, 96, 2, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido Unidad Popular'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [420,0,0,0], 0, 0, 0, 0, 0, 0,
                                                                                        [0]*2, 0, 1900, 0, 0, 0, 0, 0, 0, 0, 0, 24]) 
        # Faltan las siguientes votaciones regionales
        # ANAP
        # partido progresista femenino : 630
        # fenafui
        # partido femenino : 8972 (parte del fenafui)
        # union nacional de trabajadores : 9352
        #
        # otros        
        # union nacional de jubilados : 6831
        # democratico nacional : 2603
        # nueva accion publica : 1523
        # comerciantes frutos del país : 1273
        # organizacion campesina : 700
        # movimiento socialcristiano : 434
        # partido nacional araucano : 303
        # independientes : 2359


    if eleccion == 1949:         
        # TOTALES DIPUTADOS (Aldunate, p.192)
        # En Osorno, Llanquihue-Aysén, Chiloé y magallanes se usa Urzúa Valenzuela.
        # TOTALES SENADORES (Urzúa Valenzuela, p.551)        
        pp = pd.merge(pd.DataFrame.from_records([(d,l,p) for d in provincias for p,l in pl], columns = ['Provincias', 'Lista/Pacto', 'Partido'] ),
                      pd.DataFrame({'Total': flatten_list([9753, 12625, 7287, 16147, 11888, 45387, [56621,20486,29736,16235], 19461, 11630, 6974, 14241, 7755, 12410,
                                                          [20332]*2, 30787, 6012, 12407, 13878, 28673, 18738, 10822, 11196, 6951, 1019, 5421]) if (rep == 0) else [23620, 133569, 40993, 54721],
                                    'Provincias': provincias}),
                      how="outer")
        agg = [0,0] 

        # DETALLE DIPUTADOS (Urzúa Valenzuela, p.550)
        # conservador (socialcristiano)        
        # Laborista : 104 en Antofagasta
        # agrario laborista : 1205 en Maule, todo está corrido en 1 después
        # partido democratico del pueblo : 92 en nuble (pdba)
        # radicales : 8598 en nuble (typo)
        # socialista autentico: 0 en chiloe (vs 496)
        # socialista popular : 85+35=120 en vez de 205 en llanquihue-aysen
        # santiago-3 : errores en falange, radical, pal, democratico, radical democratico, MSC, liberal. Completados con los totales de nohlen.
        #
        # DETALLE SENADORES (Urzúa Valenzuela, p.551)
        
        pp.loc[pp['Partido'] == siglas['Partido Agrario Laborista'],'Votos'] = flatten_list([13, 0, 0, 1, 184, 1606, [5315,1952,3655,1204], 2493, 0, 1077, 2374, 1205, 1933, 
                                                                                             [1432]*2, 619, 0, 1821, 1734, 5544, 1947, 1100, 1395, 0, 138, 0]) if (rep == 0) else [0, 26920, 5530, 9780]
        pp.loc[pp['Partido'] == siglas['Partido Conservador Social Cristiano'],'Votos'] = flatten_list([0, 811, 1645, 2151, 3018, 10952, [13167,5493,6300,6640], 7596, 4981, 1591, 3811, 0, 2926,
                                                                                                      [2681]*2, 6295, 1530, 1686, 1104, 5638, 1086, 1800, 3485, 1544, 34, 153]) if (rep == 0) else [2316, 34832, 9961, 8716]
        pp.loc[pp['Partido'] == siglas['Partido Democrático'],'Votos'] = flatten_list([0, 1378, 37, 84, 182, 2136, [3159,778,1348,0], 9, 0, 69, 122, 84, 1,
                                                                                     [686]*2, 3705, 875, 705, 1083, 2017, 2155, 0, 69, 0, 0, 0]) if (rep == 0) else [0, 5649, 68, 3535]
        pp.loc[pp['Partido'] == siglas['Falange Nacional'],'Votos'] = flatten_list([1398, 1771, 1005, 916, 441, 1075, [2034,353,1249,946], 1507, 0, 0, 482, 205, 371,
                                                                                  [235]*2, 992, 0, 827, 269, 687, 962, 0, 0, 496, 0, 0]) if (rep == 0) else [2222, 0, 0, 0]       
        pp.loc[pp['Partido'] == siglas['Partido Liberal'],'Votos'] = flatten_list([2371, 1932, 0, 5393, 4439, 7663, [8321,1813,5440,2257], 2612, 3500, 1723, 3763, 2567, 4294,
                                                                                 [1449]*2, 4899, 0, 1842, 2681, 3661, 5047, 1603, 2281, 1801, 230, 0]) if (rep == 0) else [7369, 15381, 13383, 6797]
        pp.loc[pp['Partido'] == siglas['Partido Liberal Progresista'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [0]*4, 0, 0, 0, 0, 0, 0,
                                                                                             [0]*2, 0, 0, 983, 2629, 2819, 0, 0, 0, 0, 0, 0]) if (rep == 0) else [0, 0, 0, 6002]
        pp.loc[pp['Partido'] == siglas['Partido Radical'],'Votos'] = flatten_list([2368, 3714, 3608, 5111, 2834, 9598, [8262,3099,4812,2849], 2265, 2010, 1952, 2308, 1714, 2492,
                                                                                 [8598]*2, 8669, 2123, 1887, 1997, 3192, 3969, 3778, 2683, 2028, 461, 2488]) if (rep == 0) else [8443, 17627, 8200, 7855]
        pp.loc[pp['Partido'] == siglas['Partido Radical Democrático'],'Votos'] = flatten_list([1400, 269, 0, 424, 0, 1677, [2028,922,51,79], 722, 866, 222, 93, 451, 270,
                                                                                             [899]*2, 1070, 600, 1718, 1533, 2214, 1753, 1678, 1143, 1076, 90, 0]) if (rep == 0) else [0, 1031, 3612, 5802]
        pp.loc[pp['Partido'] == siglas['Partido Radical Doctrinario'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 334, [1049,0,807,2], 0, 0, 0, 0, 0, 0,
                                                                                             [0]*2, 0, 0, 0, 404, 1828, 0, 0, 0, 0, 0, 0]) if (rep == 0) else [0, 3822, 0, 4791]
        pp.loc[pp['Partido'] == siglas['Partido Socialista'],'Votos'] = flatten_list([282, 554, 79, 495, 146, 2074, [4077,1816,1294,379], 1132, 94, 0, 35, 0, 18,
                                                                                    [190]*2, 1731, 0, 405, 0, 139, 722, 14, 0, 0, 0, 0]) if (rep == 0) else [598, 5972, 195, 53]
        pp.loc[pp['Partido'] == siglas['Partido Socialista Popular'],'Votos'] =  flatten_list([475, 536, 714, 1055, 644, 1387, [3112,1724,1950,1117], 1125, 179, 340, 864, 0, 103,
                                                                                             [523]*2, 941, 502, 433, 110, 605, 437, 849, 85, 6, 35, 2780]) if (rep == 0) else [1786, 5743, 12, 1231]
        pp.loc[pp['Partido'] == siglas['Partido Socialista Auténtico'],'Votos'] = flatten_list([0, 852, 199, 517, 0, 397, [313,2089,0,19], 0, 0, 0, 369, 0, 0,
                                                                                              [0]*2, 28, 0, 0, 334, 7, 1, 0, 0, 0, 0, 0]) if (rep == 0) else [733, 14585, 0, 0]
        if rep == 0:
            pp.loc[pp['Partido'] == siglas['Acción Renovadora de Chile'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [1985,0,0,0], 0, 0, 0, 0, 0, 0,
                                                                                                [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            pp.loc[pp['Partido'] == siglas['Partido Conservador Tradicionalista'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 3846, [0,0,0,0], 0, 0, 0, 0, 0, 0,
                                                                                                         [3639]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])          
            pp.loc[pp['Partido'] == siglas['Partido Demócrata'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 1994, [0,0,0,0], 0, 0, 0, 0, 0, 0,
                                                                                       [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])            
            pp.loc[pp['Partido'] == siglas['Partido Democrático del Pueblo'],'Votos'] = flatten_list([1446, 704, 0, 0, 0, 633, [1932,248,359,741], 0, 0, 0, 15, 0, 0,
                                                                                                    [0]*2, 1836, 0, 98, 0, 320, 118, 0, 55, 0, 31, 0])   
            pp.loc[pp['Partido'] == siglas['Partido Laborista'],'Votos'] = flatten_list([0, 104, 0, 0, 0, 15, [1571,49,2428,2], 0, 0, 0, 5, 0, 2,
                                                                                       [0]*2, 2, 382, 2, 0, 2, 541, 0, 0, 0, 0, 0])              
            pp.loc[pp['Partido'] == siglas['Movimiento Social Cristiano'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [296,150,43,0], 0, 0, 0, 0, 1529, 0,
                                                                                                 [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])            
    
    if eleccion == 1945:    
        # TOTALES DIPUTADOS (Aldunate, p.179)
        # Notar que Aconcagua, Ñuble y Osorno no coinciden con Urzúa Valenzuela.
        pp = pd.merge(pd.DataFrame.from_records([(d,l,p) for d in provincias for p,l in pl], columns = ['Provincias', 'Lista/Pacto', 'Partido'] ),
                      pd.DataFrame({'Total': flatten_list([9371, 15082, 5224, 19298, 12460, 45087, [59126,17785,23645,15719], 17507, 12561, 7651, 14556, 6511, 13260,
                                                          [6807,13380], 28695, 5718, 12125, 13819, 24882, 17447, 9722, 10046, 6259, 976, 5211]),
                                    'Provincias': provincias}),
                      how="outer")
        
        # DETALLE DIPUTADOS (Urzúa Valenzuela, p.538)
        # total : 449930 vs 449916 nohlen, totales partidarios coinciden con Nohlen (excepto PL e IND)
        # Progresista Nacional (comunistas)        
        # Democrático : +1 en nuble
        # Liberal : +20 en linares (pdba), total de 80597 (typo en Nohlen?)
                
        pp.loc[pp['Partido'] == siglas['Partido Agrario'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [247,0,0,0], 0, 0, 0, 809, 0, 2902,
                                                                                 [0,688], 0, 0, 0, 0, 4104, 0, 0, 0, 0, 0, 0])
        pp.loc[pp['Partido'] == siglas['Alianza Popular Libertadora'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 1531, [883,518,1212,0], 0, 0, 610, 0, 0, 0,
                                                                                             [0]*2, 0, 0, 0, 0, 1543, 0, 0, 0, 0, 0, 0])
        pp.loc[pp['Partido'] == siglas['Partido Conservador'],'Votos'] = flatten_list([0, 991, 1858, 1116, 3099, 12496, [13414,6280,6698,6974], 6656, 5433, 1881, 4288, 1986, 2924,
                                                                                     [1679,4838], 4745, 1522, 4328, 1221, 4355, 891, 1617, 2759, 2180, 35, 0])
        pp.loc[pp['Partido'] == siglas['Partido Demócrata'],'Votos'] = flatten_list([0, 0, 0, 2565, 0, 0, [0]*4, 0, 0, 0, 0, 0, 0,
                                                                                   [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])    
        pp.loc[pp['Partido'] == siglas['Partido Demócrata Nacionalista'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 1045, [2018,267,22,0], 13, 0, 0, 0, 0, 0,
                                                                                                [1062,0], 0, 0, 0, 525, 0, 0, 0, 0, 0, 0, 0])
        pp.loc[pp['Partido'] == siglas['Partido Democrático'],'Votos'] = flatten_list([0, 1010, 0, 0, 0, 1297, [5397,607,2015,718], 97, 7, 970, 990, 0, 232,
                                                                                     [573,0], 4695, 0, 4, 0, 2425, 64, 0, 336, 0, 26, 0]) 
        pp.loc[pp['Partido'] == siglas['Falange Nacional'],'Votos'] = flatten_list([2073, 1831, 0, 224, 0, 1107, [1601,101,409,0], 1035, 875, 0, 224, 0, 0,
                                                                                  [0]*2, 0, 0, 0, 155, 892, 0, 0, 440, 533, 65, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido Laborista'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [130,0,0,0], 0, 0, 0, 0, 0, 0,
                                                                                   [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])   
        
        pp.loc[pp['Partido'] == siglas['Partido Liberal'],'Votos'] = flatten_list([1499, 1502, 0, 5260, 4110, 8294, [8632,2779,3999,2558], 3842, 3874, 1787, 4935, 2056, 3138,
                                                                                 [1485,2081], 3051, 649, 2037, 4811, 2875, 2495, 1111, 1394, 55, 288, 0])  
        
        pp.loc[pp['Partido'] == siglas['Partido Liberal Progresista'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [0]*4, 0, 0, 0, 0, 0, 0,
                                                                                             [0]*2, 0, 0, 0, 1625, 0, 3592, 1132, 1903, 1403, 194, 0])    
        pp.loc[pp['Partido'] == siglas['Partido Progresista Nacional'],'Votos'] = flatten_list([2399, 5226, 0, 3753, 1053, 4777, [7090,2251,2615,1317], 1794, 0, 723, 903, 0, 492,
                                                                                              [0,430], 6951, 1683, 0, 10, 1271, 1395, 0, 0, 0, 0, 0])
        pp.loc[pp['Partido'] == siglas['Partido Radical'],'Votos'] = flatten_list([1664, 2828, 3126, 4383, 2366, 6653, [9221,1958,2674,2165], 1043, 2014, 1680, 1972, 2469, 2823,
                                                                                 [1644,3733], 6903, 1824, 3552, 4590, 5490, 4367, 3990, 2621, 1878, 291, 0])
        pp.loc[pp['Partido'] == siglas['Partido Socialista'],'Votos'] = flatten_list([845, 597, 0, 1594, 512, 3119, [8339,1967,2573,1562], 0, 1, 0, 435, 0, 749,
                                                                                    [328,1015], 2138, 0, 1138, 549, 783, 772, 676, 0, 171, 0, 2451])       
        pp.loc[pp['Partido'] == siglas['Partido Socialista Auténtico'],'Votos'] = flatten_list([891, 1097, 240, 403, 1320, 3401, [2154,1057,1428,425], 3027, 357, 0, 0, 0, 0,
                                                                                              [36,595], 212, 40, 1066, 333, 1144, 3871, 1196, 593, 39, 77, 102])
        pp.loc[pp['Partido'] == siglas['Candidatura Independiente'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 1367, [0]*4, 0, 0, 0, 0, 0, 0,
                                                                               [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2658])             
        
    if eleccion == 1941:    
        # TOTALES DIPUTADOS (Aldunate, p.177)
        # Santiago : 113196=60850+16971+20437+14938
        # Nuble : 21275=7051+14224 (asumimos que los 60 votos faltantes corresponden a Nuble-2)
        # Malleco : typo
        #
        # TOTALES SENADORES (Urzúa Valenzuela, p.522)
        pp = pd.merge(pd.DataFrame.from_records([(d,l,p) for d in provincias for p,l in pl], columns = ['Provincias', 'Lista/Pacto', 'Partido'] ),
                      pd.DataFrame({'Total': flatten_list([11614, 18165, 7917, 19812, 12137, 43283, [60850,16971,20437,14938], 18974, 12184, 7247, 13661, 7026, 12065,
                                                          [7051,14224], 28661, 5380, 12290, 13890, 25571, 15770, 8702, 9115, 5960, 937, 5416]) if (rep == 0) else [27669, 114481, 39282, 52053],
                                    'Provincias': provincias}),
                      how="outer")

        # DETALLE DIPUTADOS (Urzúa Valenzuela, p.523)
        # Progresista Nacional (Comunistas): 2690 en vez de 2696 en O'Higgins
        # Falange : 1904 en vez de 1004 Tarapacá
        # Radical : Llanquihue-Aysén, 1842=1448+394 (pdba: error en Aysen)
        # Socialista : faltan 60 votos en Nuble, posible typo en Nuble-2 (3975 en vez de 3915). Llanquihue-Aysén : 3727=3358+369 (pdba: error en Aysen)
        #
        # DETALLE SENADORES (Urzúa Valenzuela, p.522)

        pp.loc[pp['Partido'] == siglas['Partido Agrario'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [0]*4, 0, 0, 0, 993, 0, 1522,
                                                                                 [1078,0], 0, 313, 0, 0, 3817, 0, 0, 0, 0, 0, 0]) if (rep == 0) else [0, 0, 0, 3855]     
        pp.loc[pp['Partido'] == siglas['Alianza Popular Libertadora'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 717, [260,0,0,0], 0, 0, 0, 488, 0, 0,
                                                                                             [0]*2, 4, 0, 0, 0, 0, 2121, 799, 0, 0, 0, 0]) if (rep == 0) else [0, 762, 0, 0]
        pp.loc[pp['Partido'] == siglas['Partido Conservador'],'Votos'] = flatten_list([14, 1514, 938, 1481, 2344, 7724, [10076,4248,4132,4488], 4644, 3542, 1705, 3645, 1500, 2997,
                                                                                     [1831,4230], 3500, 0, 2595, 1575, 2467, 517, 952, 2981, 1537, 66, 0]) if (rep == 0) else [0, 32010, 12177, 8263]
        pp.loc[pp['Partido'] == siglas['Partido Demócrata'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 436, [177,0,0,69], 35, 248, 38, 0, 0, 25,
                                                                                   [0]*2, 2919, 0, 72, 1037, 1333, 0, 0, 0, 0, 0, 0]) if (rep == 0) else [5, 120, 0, 2274]
        pp.loc[pp['Partido'] == siglas['Partido Democrático'],'Votos'] = flatten_list([0, 903, 0, 310, 32, 949, [4661,999,1859,876], 35, 90, 368, 215, 208, 589,
                                                                                     [0,745], 1315, 9, 1135, 826, 1637, 981, 170, 115, 148, 27, 0]) if (rep == 0) else [230, 8361, 1351, 2982]
        pp.loc[pp['Partido'] == siglas['Falange Nacional'],'Votos'] = flatten_list([1904, 1557, 0, 796, 84, 2972, [3878,597,0,0], 907, 0, 0, 445, 112, 449,
                                                                                  [127,0], 566, 0, 274, 0, 726, 0, 0, 0, 159, 0, 0]) if (rep == 0) else [1228, 0, 0, 0]
        pp.loc[pp['Partido'] == siglas['Partido Laborista'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [1306,103,3,43], 0, 0, 0, 0, 0, 0,
                                                                                            [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) if (rep == 0) else [0,5877, 0, 0] 
        pp.loc[pp['Partido'] == siglas['Partido Liberal'],'Votos'] = flatten_list([1479, 213, 624, 4142, 2956, 7198, [4985,1689,2433,2056], 3222, 2262, 1614, 1891, 2323, 1771,
                                                                                 [1083,2077], 1524, 592, 2338, 3612, 3683, 2136, 948, 1058, 1041, 47, 0]) if (rep == 0) else [6873, 12391, 8630, 10071]
        pp.loc[pp['Partido'] == siglas['Partido Progresista Nacional'],'Votos'] = flatten_list([3702, 7514, 0, 4136, 1825, 5466, [6591,1989,2340,1421], 2690, 429, 1218, 1797, 0, 0,
                                                                                              [0,784], 5773, 1880, 0, 671, 1078, 1365, 286, 155, 0, 34, 0]) if (rep == 0) else [5676, 16572, 4088, 2113]
        pp.loc[pp['Partido'] == siglas['Partido Radical'],'Votos'] = flatten_list([2206, 3160, 4360, 5729, 2750, 7141, [9003,1965,3462,2322], 2846, 1934, 1368, 1987, 2407, 2197,
                                                                                 [1600,3975], 6252, 1599, 3768, 4006, 6313, 3481, 1475, 1448, 2230, 394, 2041]) if (rep == 0) else [9113, 17576, 8164, 14866]
        pp.loc[pp['Partido'] == siglas['Partido Socialista'],'Votos'] = flatten_list([1845, 2855, 1684, 2910, 2146, 7928, [10559,3217,3930,3140], 3379, 3562, 936, 1709, 401, 2049,
                                                                                    [656,1709], 2687, 987, 2108, 1689, 3620, 4111, 3672, 3358, 845, 369, 2316]) if (rep == 0) else [4544, 20812, 4872, 7629]  
        if rep == 0:
            pp.loc[pp['Partido'] == siglas['Partido Laborista Proletario'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [64,0,0,1], 0, 0, 0, 0, 0, 0,
                                                                                                  [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])       
            pp.loc[pp['Partido'] == siglas['Partido Radical Socialista'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 381, [2699,668,218,0], 0, 0, 0, 0, 75, 12,
                                                                                                [676,324], 0, 0, 0, 0, 23, 0, 0, 0, 0, 0, 0])
            pp.loc[pp['Partido'] == siglas['Partido Radical Socialista Obrero'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [456,0,0,0], 0, 0, 0, 0, 0, 0,
                                                                                                         [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])       
            pp.loc[pp['Partido'] == siglas['Partido Regionalista de Magallanes'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [0]*4, 0, 0, 0, 0, 0, 0,
                                                                                                         [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1058])       
            pp.loc[pp['Partido'] == siglas['Partido Socialista de Trabajadores'],'Votos'] = flatten_list([396, 449, 311, 308, 0, 924, [2667,1204,378,58], 947, 117, 0, 123, 0, 454,
                                                                                                        [0,380], 3368, 0, 0, 0, 54, 313, 75, 0, 0, 0, 1])
            pp.loc[pp['Partido'] == siglas['Vanguardia Popular Socialista'],'Votos'] = flatten_list([68, 0, 0, 0, 0, 1447, [3468,292,1682,464], 269, 0, 0, 368, 0, 0,
                                                                                                   [0]*2, 753, 0, 0, 474, 820, 745, 325, 0, 0, 0, 0])
    
    if eleccion == 1937:         
        # TOTALES DIPUTADOS (Urzúa Valenzuela, p.495).
        # TOTALES SENADORES (Urzúa Valenzuela, p.497).
        pp = pd.merge(pd.DataFrame.from_records([(d,l,p) for d in provincias for p,l in pl], columns = ['Provincias', 'Lista/Pacto', 'Partido'] ),
                      pd.DataFrame({'Total': flatten_list([10152, 15314, 6683, 18583, 10913, 40472, [57298,15007,18682,13003], 17231, 11409, 6405, 13420, 6851, 11376,
                                                          [7103,13677], 25457, 4612, 18994, 9757, 21404, 20880, 8308, 5442, 3880]) if (rep == 0) else [25631, 50316, 28022, 49698, 38039],
                                    'Provincias': provincias}),
                      how="outer")

        # DETALLE DIPUTADOS (Urzúa Valenzuela, p.495).
        # Partido Nacional Democratico (comunista).
        #
        # DETALLE SENADORES (Urzúa Valenzuela, p.497).
        
        pp.loc[pp['Partido'] == siglas['Partido Acción Republicana'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 1590, [2670,0,1454,0], 0, 0, 0, 0, 0, 0,
                                                                                             [0]*2, 597, 0, 0, 0, 1564, 1627, 0, 0, 0]) if (rep == 0) else [4377, 7530, 4974, 14373, 11179]
        pp.loc[pp['Partido'] == siglas['Partido Agrario'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [0]*4, 0, 0, 939, 0, 1668, 0,
                                                                                  [0,1108], 0, 0, 1301, 4705, 0, 0, 0, 0, 0]) if (rep == 0) else [0, 0, 0, 0, 2187]   
        pp.loc[pp['Partido'] == siglas['Partido Conservador'],'Votos'] = flatten_list([1336, 1543, 1520, 3330, 2830, 7767, [9105,4282,4707,3909], 5735, 3743, 3203, 3711, 3112, 2471,
                                                                                      [1822,4357], 3697, 0, 3331, 2537, 2008, 3065, 3585, 1839, 0]) if (rep == 0) else [3148, 8811, 11767, 10479, 7268] 
        pp.loc[pp['Partido'] == siglas['Partido Demócrata'],'Votos'] = flatten_list([1190, 0, 6, 94, 2145, 3755, [622,740,382,571], 307, 0, 0, 0, 26, 771,
                                                                                    [302,2879], 778, 1190, 1424, 2362, 387, 52, 43, 0, 0]) if (rep == 0) else [10, 2808, 1322, 2733, 131]
        pp.loc[pp['Partido'] == siglas['Partido Democrático'],'Votos'] = flatten_list([0, 0, 1310, 607, 0, 0, [1269,1328,694,846], 796, 0, 0, 0, 0, 533,
                                                                                      [0,1355], 1976, 934, 2595, 0, 1278, 2545, 602, 0, 0]) if (rep == 0) else [5758, 0, 0, 0, 0]
        pp.loc[pp['Partido'] == siglas['Partido Liberal'],'Votos'] = flatten_list([1679, 1639, 5043, 5384, 6226, 7164, [149,2154,4281,5050], 3545, 189, 4768, 2443, 4664, 1792,
                                                                                  [4003,1420], 1211, 6644, 2233, 2254, 4977, 1983, 1279, 315, 0]) if (rep == 0) else [6134, 11310, 5302, 10858, 12619]
        pp.loc[pp['Partido'] == siglas['Partido Nacional Democrático'],'Votos'] = flatten_list([2094, 3528, 253, 0, 0, 4275, [3737,0,0,0], 1038, 0, 0, 0, 0, 0,
                                                                                               [0,0], 1944, 0, 0, 0, 293, 0, 0, 0, 0]) if (rep == 0) else [1229, 4429, 1774, 0, 111]
        pp.loc[pp['Partido'] == siglas['Movimiento Nacional Socialista'],'Votos'] = flatten_list([0, 258, 0, 0, 0, 2714, [4141,671,1628,982], 0, 0, 0, 0, 0, 0,
                                                                                                 [0,239], 0, 0, 0, 0, 1729, 1479, 652, 49, 0]) if (rep == 0) else [1448, 0, 0, 2410, 0]    
        pp.loc[pp['Partido'] == siglas['Partido Radical'],'Votos'] = flatten_list([1771, 8261, 1948, 6149, 2575, 6411, [7800,1461,2542,1790], 1703, 841, 1283, 3400, 1046, 1638,
                                                                                  [2125,3421], 5195, 1680, 5125, 2748, 2716, 5206, 1524, 1564, 0]) if (rep == 0) else [3400, 12850, 2881, 4594, 2468]            
        # pp.loc[pp['Partido'] == siglas['Partido Radical Socialista'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [0,0,0,0], 0, 0, 0, 0, 0, 0,
        #                                                                                      [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0])   
        pp.loc[pp['Partido'] == siglas['Partido Socialista'],'Votos'] = flatten_list([1500, 2501, 0, 3401, 0, 5146, [13167,5151,5785,719], 1304, 377, 0, 0, 0, 396,
                                                                                     [0]*2, 3441, 0, 0, 514, 1132, 1196, 0, 0, 2215]) if (rep == 0) else [0, 0, 0, 4251, 2052]
        pp.loc[pp['Partido'] == siglas['Candidatura Independiente'],'Votos'] = flatten_list([3212, 1224, 1, 0, 0, 391, [2885,0,972,0], 0, 2596, 0, 0, 0, 0,
                                                                                [0]*2, 3171, 0, 0, 0, 586, 3, 0, 668, 1330]) if (rep == 0) else [0, 2578, 0, 0, 0]


    if rep == 0:    
        ## los datos de santiago y nuble vienen por agrupacion departamental, pero en general los totales son provinciales
        if agg[0] == 1:
            aux = pp[(pp['Provincias'].str.contains('Santiago')) & (pp['Partido'] != '')].groupby(['Lista/Pacto', 'Partido']).agg({'Votos':'sum'}).reset_index()   
            pp.loc[(pp['Provincias'] == 'Santiago-1') & (pp['Partido'] != ''), aux.columns.tolist()] = aux.loc[:, aux.columns.tolist()].values
            pp.loc[(pp['Provincias'] == 'Santiago-2') & (pp['Partido'] != ''), aux.columns.tolist()] = aux.loc[:, aux.columns.tolist()].values
            pp.loc[(pp['Provincias'] == 'Santiago-3') & (pp['Partido'] != ''), aux.columns.tolist()] = aux.loc[:, aux.columns.tolist()].values
            pp.loc[(pp['Provincias'] == 'Santiago-4') & (pp['Partido'] != ''), aux.columns.tolist()] = aux.loc[:, aux.columns.tolist()].values   
          
        if agg[1] == 1:
            aux = pp[(pp['Provincias'].str.contains('Ñuble')) & (pp['Partido'] != '')].groupby(['Lista/Pacto', 'Partido']).agg({'Votos':'sum'}).reset_index()   
            pp.loc[(pp['Provincias'] == 'Ñuble-1') & (pp['Partido'] != ''), aux.columns.tolist()] = aux.loc[:, aux.columns.tolist()].values
            pp.loc[(pp['Provincias'] == 'Ñuble-2') & (pp['Partido'] != ''), aux.columns.tolist()] = aux.loc[:, aux.columns.tolist()].values

        ## las provincias de Llanquihue y Aysen forman una agrupación departamental
        if 1941 <= eleccion <= 1965:
            pp['Provincias'] = pp['Provincias'].replace({'Llanquihue':'Llanquihue y Aysén', 'Aysén':'Llanquihue y Aysén'})
            pp = pp.groupby(['Provincias', 'Lista/Pacto', 'Partido']).sum().reset_index()
    
    return pp