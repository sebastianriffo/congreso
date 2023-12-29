#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from modulos.pactos import pactos_electorales, siglas_partidos
from modulos.resultados.correcciones1925_1969 import correcciones1925_1969
from modulos.resultados.correcciones1891_1924 import correcciones1891_1924
from modulos.resultados.correcciones1828_1888 import correcciones1828_1888

import pandas as pd
pd.options.mode.chained_assignment = None

from pathlib import Path
import re
from operator import itemgetter
from ast import literal_eval

def parlamentarios1828_1969(path_datos, candidatos, eleccion, rep, siglas=None):
    """

    Parámetros
    ----------
    path_datos : PosixPath
        Directorio.    
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

    if rep == 1 and (eleccion not in {1834,1925,1932}) and not bool(sorted(path_datos.glob('*Circunscripcion*_electos.csv'))):        
        if (eleccion >= 1925):
            path_datos_prev = path_datos.parents[0]/str(eleccion-(4+(eleccion in {1930,1937})))
            datos_filenames = sorted(path_datos_prev.glob('*Circunscripcion*_electos.csv'))
            electos_prev = pd.read_csv(datos_filenames[0]) 
            electos_prev['Candidatos'] = electos_prev['Candidatos'].apply(lambda x : literal_eval(str(x))).apply(' '.join)
            
            #corregir
            electos_prev = electos_prev[electos_prev['Circunscripción'].isin([2,4,6,8,10] if (eleccion -1937)%8 == 0 else [1,3,5,7,9])]
            
            candidatos = pd.concat([candidatos, electos_prev], axis=0)
            candidatos = candidatos[~candidatos['Candidatos'].str.lower().duplicated(keep="last")]
    
            candidatos = candidatos[candidatos['Electos_comp'] == '*']  
            candidatos['Electos'] = '*'
            candidatos = candidatos.fillna('')

    if rep == 1 and (1876 > eleccion >= 1834):
        if eleccion == 1834:
            # 1834-1840, a renovar en dos períodos
            t2 = ['Juan Francisco Meneses Echanes',
                  'Pedro Ovalle Landa',
                  'Manuel Rengifo Cárdenas',
                  'Agustín Vial Santelices',
                  'Fernando Antonio Elizalde Marticorena',
                  'José Miguel Irarrázaval Alcalde',
                  'Diego Antonio Barros Fernández']
            
            # 1834-1837, a renovar el próximo período
            t3 = ['Juan Agustín Alcalde Bascuñán',
                  'Juan de Dios Vial del Río',
                  'José Ignacio Eyzaguirre Arechavala',
                  'José María de Rozas Lima Melo', #corregir 
                  'Fernando Errázuriz Aldunate',
                  'Diego Antonio Elizondo Prado',
                  'Estanislao Segundo Portales Larraín']
        else:
            path_datos_prev = path_datos.parents[0]/str(eleccion-3)
            datos_filenames = sorted(path_datos_prev.glob('*Circunscripcion*_electos.csv'))
            electos_prev = pd.read_csv(datos_filenames[0]).fillna('')
            electos_prev['Candidatos'] = electos_prev['Candidatos'].apply(lambda x : literal_eval(str(x))).apply(' '.join)
            
            electos_prev = electos_prev[electos_prev['Circunscripción'].isin(['Nacional-1', 'Nacional-2'])].replace({'Nacional-2':'Nacional-3', 'Nacional-1':'Nacional-2'})
           
            t2 = electos_prev.loc[electos_prev['Circunscripción'].isin(['Nacional-2']), 'Candidatos'].values.tolist()
            t3 = electos_prev.loc[electos_prev['Circunscripción'].isin(['Nacional-3']), 'Candidatos'].values.tolist()

        candidatos.loc[~candidatos['Candidatos'].isin(t2) & ~candidatos['Candidatos'].isin(t3), 'Circunscripción'] = 'Nacional-1'
        candidatos.loc[candidatos['Candidatos'].isin(t2), 'Circunscripción'] = 'Nacional-2'        
        candidatos.loc[candidatos['Candidatos'].isin(t3), 'Circunscripción'] = 'Nacional-3'        

        if eleccion > 1834:        
            candidatos = pd.concat([candidatos, electos_prev], axis=0)
            candidatos = candidatos[~candidatos['Candidatos'].str.lower().duplicated(keep="last")]

    ## cambios en candidatos    
    if eleccion >= 1828:    
        if eleccion >= 1925: 
            (candidatos, reemplazados, reemplazantes, presuntivos, militancia) = correcciones1925_1969(candidatos, eleccion, rep) 
            filename = path_datos.parents[1] / 'Diputados_1925-1973.csv'
        elif eleccion >= 1891:
            (candidatos, reemplazados, reemplazantes, presuntivos, militancia) = correcciones1891_1924(candidatos, eleccion, rep)
            filename = path_datos.parents[1] / ('Diputados_1891-1924.csv' if rep == 0 else 'Senado_1828-1924.csv')
        else:
            (candidatos, reemplazados, reemplazantes, presuntivos, militancia) = correcciones1828_1888(candidatos, eleccion, rep)
            filename = path_datos.parents[1] / ('Diputados_1828-1888.csv' if rep == 0 else 'Senado_1828-1924.csv')

        candidatos.loc[candidatos['Candidatos'].str.contains('|'.join(reemplazados)), 'Electos_comp'] = None
        
        candidatos.loc[candidatos['Candidatos'].str.contains('|'.join(reemplazantes)), 'Electos'] = None
        candidatos.loc[candidatos['Candidatos'].str.contains('|'.join(presuntivos)), ['Electos', 'Electos_comp']] = [None, None]
    
        for partido, parlamentarios in militancia.items():        
            candidatos.loc[candidatos['Candidatos'].str.contains('|'.join(parlamentarios)), 'Partido'] = siglas[partido] if siglas else partido
        
    #verificar titulares
    if ((rep == 0) and (eleccion >= 1828)) or ((rep == 1) and (eleccion <= 1831 or 1876 <= eleccion < 1925)):        
        candidatos.loc[candidatos['Electos'] != '*', 'Electos'] = None

        total = pd.read_csv(filename, index_col=0).fillna(0).astype(int)        
        col = str([int(x) for x in total.columns.tolist() if int(x) <= eleccion][-1])        
        # provincias = candidatos[subdivrow].unique().tolist()
        provincias = total.index.unique().tolist()
                
        row = list(filter(re.compile('|'.join(provincias)).findall, total.index.unique().tolist() ))
                
        count = (candidatos.groupby([subdivrow])['Electos'].count().to_frame()).join(total[total.index.isin(row)].loc[total[col]>0, col])
        count = count.fillna(0).astype(int)
        
        count['diff'] = count['Electos'] -count[col]
              
        if not count[count['diff'] != 0].empty:
            print('DESAJUSTES '+str(eleccion))
            print(count[count['diff'] != 0])
            print('')
        # print('PARTIDOS')
        # print(candidatos[candidatos['Electos'] == '*'].groupby(['Partido'])['Electos'].count().to_frame())


    #verificar suplentes
    if ((rep == 0) and (1829 <= eleccion <= 1888)) or (rep == 1 and (eleccion == 1831 or 1876 <= eleccion <= 1888)):

        total = pd.read_csv(path_datos.parents[1] / ('Diputados_(s)_1829-1888.csv' if rep == 0 else 'Senado_(s)_1831-1888.csv'), index_col=0).fillna(0).astype(int)        
        col = str([int(x) for x in total.columns.tolist() if int(x) <= eleccion][-1])        
                
        count = (candidatos[candidatos['Electos'] != '*'].groupby([subdivrow])['Electos_comp'].count().to_frame()).join(total[total.index.isin(row)].loc[total[col]>0, col])
        count = count.fillna(0).astype(int)
        
        count['diff'] = count['Electos_comp'] -count[col]
        if not count[count['diff'] != 0].empty:                
            print('DESAJUSTES SUPLENTES')
            print(count[count['diff'] != 0])
            print('')

    return candidatos