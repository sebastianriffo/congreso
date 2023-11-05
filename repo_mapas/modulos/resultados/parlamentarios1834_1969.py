#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from modulos.pactos import pactos_electorales, siglas_partidos
from modulos.resultados.correcciones1925_1969 import correcciones1925_1969
from modulos.resultados.correcciones1891_1924 import correcciones1891_1924
from modulos.resultados.correcciones1833_1888 import correcciones1833_1888

import pandas as pd
pd.options.mode.chained_assignment = None

from pathlib import Path
import re
from operator import itemgetter
from ast import literal_eval

def parlamentarios1834_1969(path_datos, candidatos, eleccion, rep, siglas=None):
    """
    Corrección de datos electorales en el período 1925-1969, a partir de información
    obtenida del diario La Nación y wikipedia.

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
        
    Entrega
    -------
    candidatos    
    
    """
        
    subdivrow = {0:'Distrito',1:'Circunscripción'}[rep]
    reemplazados, reemplazantes = [], []

    if rep == 1 and (eleccion >= 1925) and (eleccion not in {1925,1932}) and not bool(sorted(path_datos.glob('*Circunscripcion*_electos.csv'))): 
        path_datos_prev = path_datos.parents[0]/str(eleccion-(4+(eleccion in {1930,1937})))
        datos_filenames = sorted(path_datos_prev.glob('*Circunscripcion*_electos.csv'))
        electos_prev = pd.read_csv(datos_filenames[0]) 
        electos_prev['Candidatos'] = electos_prev['Candidatos'].apply(lambda x : literal_eval(str(x))).apply(' '.join)
        
        electos_prev = electos_prev[electos_prev['Circunscripción'].isin([2,4,6,8,10] if (eleccion -1937)%8 == 0 else [1,3,5,7,9])]
        
        candidatos = pd.concat([candidatos, electos_prev], axis=0)
        candidatos = candidatos[~candidatos['Candidatos'].str.lower().duplicated(keep="last")]

        candidatos = candidatos[candidatos['Electos_comp'] == '*']  
        candidatos['Electos'] = '*'
        candidatos = candidatos.fillna('')

    ## cambios en candidatos    
    if eleccion >= 1828:    
        if eleccion >= 1925: 
            (candidatos, reemplazados, reemplazantes, presuntivos, militancia) = correcciones1925_1969(candidatos, eleccion, rep) 
        elif eleccion >= 1891:
            (candidatos, reemplazados, reemplazantes, presuntivos, militancia) = correcciones1891_1924(candidatos, eleccion, rep)
        else:
            (candidatos, reemplazados, reemplazantes, presuntivos, militancia) = correcciones1833_1888(candidatos, eleccion, rep)

        candidatos.loc[candidatos['Candidatos'].str.contains('|'.join(reemplazados)), 'Electos_comp'] = None
        candidatos.loc[candidatos['Candidatos'].str.contains('|'.join(reemplazantes)), 'Electos'] = None
        candidatos.loc[candidatos['Candidatos'].str.contains('|'.join(presuntivos)), ['Electos', 'Electos_comp']] = [None, None]
    
        for partido, parlamentarios in militancia.items():        
            candidatos.loc[candidatos['Candidatos'].str.contains('|'.join(parlamentarios)), 'Partido'] = siglas[partido] if siglas else partido

        # if eleccion >= 1932:    
        #     candidatos[subdivrow] = candidatos[subdivrow].astype(int)  
        
    #verificar si están todos los diputados
    if False and (rep == 0) and (eleccion >= 1828):
        candidatos.loc[candidatos['Electos'] != '*', 'Electos'] = None
        count = candidatos.groupby(['Distrito'])['Electos'].count().to_frame()
        # count = candidatos[candidatos['Electos'] == '*'].groupby(['Distrito']).agg({'Electos':'count'})
        
        if eleccion >= 1969:
            count['escanos'] = [4,7,2,7,3,12,5,6,4,3,5,3,4,3,5,9,2,4,6,10,5,3,3,3,2,2,18,5,5]
        elif eleccion >= 1941:
            count['escanos'] = [4,7,2,7,3,12,5,6,4,3,5,3,4,3,5,9,2,4,6,10,5,3,3,3,1,18,5,5]
        elif eleccion == 1937:
            count['escanos'] = [4,7,2,7,3,12,5,6,4,3,5,3,4,3,5,9,2,6,4,9,8,3,3,1,18,5,5]
        elif eleccion == 1932:
            count['escanos'] = [4,7,2,7,3,12,4,6,4,3,4,2,4,3,5,7,4,6,4,9,8,3,3,1,18,5,5]
        elif eleccion == 1930:
            count['escanos'] = [5,6,2,7,5,11,18,5,4,6,4,5,4,4,6,5,4,3,4,4,6,7,4,4]
        elif eleccion == 1925:
            count['escanos'] = [4,6,2,7,5,11,18,5,4,6,4,5,4,4,6,5,4,3,4,4,6,7,4,4]       
        elif eleccion >= 1912:
            count['escanos'] = [4,2,2,3,3,4,2,3,3,7,13,4,3,3,3,2,2,3,2,2,2,3,2,2,2,2,2,3,2,1,3,4,2,2,4,4,2,2,2,2]
        elif eleccion == 1909: 
            count['escanos'] = [2,2,3,3,4,2,3,3,4,8,3,3,3,3,3,4,4,3,2,3,2,3,4,3,4,3,3,2,3,3]
        elif eleccion >= 1891: 
            count['escanos'] = [2,2,3,3,4,2,3,3,4,8,3,3,3,3,3,4,4,3,2,3,2,3,4,3,4,3,2,2,3,3]
        elif eleccion == 1888:
            count['escanos'] = [1,2,1,1,2,1,1,2,1,1,3,1,1,2,1,2,2,1,2,1,6,1,12,2,3,1,2,1,4,4,2,3,3,1,2,2,2,1,2,2,2,2,3,1,1,2,1,2,2,2,1,1,1,1,2,2,1,1,1,1,1,2,1,1,1,1,1,1,2]
        elif eleccion == 1885:
            count['escanos'] = [1,2,1,1,2,1,1,1,1,1,3,1,2,2,1,2,2,1,2,1,5,1,10,2,3,1,2,1,4,4,
                                2,3,3,1,1,3,1,2,2,2,2,2,3,1,1,1,0,2,2,2,1,1,1,1,2,1,1,1,1,1,1,1,2,1]
        elif eleccion >= 1876:
            count['escanos'] = [2,1,1,1,1,1,3,1,2,2,1,2,2,1,2,1,5,1,10,2,2,5,4,4,2,3,5,1,3,1,2,2,2,2,2,5,1,1,2,1,1,
                                1,1,1,1,2,1,1,1,1,1,1,1,2,1]
        elif eleccion >= 1867:
            count['escanos'] = [1,2,1,1,1,1,1,2,1,2,2,1,1,1,1,2,1,4,1,8,2,1,5,4,4,2,3,4,1,3,1,3,1,2,2,4,2,2,2,1,1,
                                1,1,2,1,1,1,1,1,1,1]
        elif eleccion == 1864:
            count['escanos'] = [2,1,0,1,1,2,1,1,1,1,1,1,1,2,3,1,6,2,1,4,3,3,4,3,1,2,1,3,2,1,4,1,1,1,1,1,1,1,1,1,1,1,1,1,1]            
            
        elif eleccion >= 1855:
            count['escanos'] = [2,1,0,1,1,2,1,1,1,1,1,1,1,2,3,1,6,2,1,4,3,3,4,3,1,2,1,3,2,1,4,1,1,1,1,1,1,1,1,1,1,1,1]   
            
        elif eleccion >= 1834:
            count['escanos'] = [1,1,1,1,1,1,1,1,1,1,1,2,1,1,7,1,2,2,3,2,2,2,1,2,1,2,2,1,1,1,1,1,2,1,1,1,1,1]

        elif eleccion == 1831:
            count['escanos'] = [1,1,1,2,1,
                                1,1,1,1,2,
                                1,1,7,1,1,
                                5,2,2,
                                2,1,2,1,2,
                                2,1,1,1,0,1,
                                2,
                                1,0,
                                0,1,1]

        elif eleccion == 1829:
            count['escanos'] = [1,1,2,0,1,1,1,1,2,2,1,1,7,1,2,5,2,2,2,1,1,1,2,2,1,1,1,1,1,2,1,1,1,1,0]

        elif eleccion == 1828:
            count['escanos'] = [0,1,1,1,0,
                                1,1,1,2,1,
                                0,2,5,1,1,
                                3,2,1,
                                2,0,1,1,1,
                                2,1,1,0,0,1,
                                2,
                                1,1,
                                1,1,0]            
            
        count['diff'] = count['Electos'] -count['escanos']
        
        print('TOTAL : ', count['escanos'].sum())
    
        print('DESAJUSTES')
        print(count[count['diff'] != 0])
        print(candidatos[candidatos['Distrito'].isin(count[count['diff'] != 0].index)][['Distrito','Candidatos']].sort_values(['Candidatos']).sort_values(['Distrito']))
    
        print('')
        
        # if eleccion >= 1891:
        #     print('REEMPLAZOS')        
        #     print(candidatos[(candidatos['Electos_comp'] == '*') & (candidatos['Electos'] != '*')]['Candidatos'])

    return candidatos