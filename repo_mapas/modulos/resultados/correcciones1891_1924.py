#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
pd.options.mode.chained_assignment = None

from pathlib import Path
import re
from operator import itemgetter
from ast import literal_eval

from pactos import pactos_electorales, siglas_partidos
from resultados_miscelaneo import nombres_formato

def elecciones1891_1924(candidatos, eleccion, rep):
    """
    Corrección de datos electorales en el período 1891-1924, a partir de información
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

    if eleccion == 1924:
        #elecciones complementarias
        reemplazados = []#['Pontigo Urrutia', 'Lacoste Navarro', 'Avendaño Ortúzar']
        reemplazantes = []#['Altamirano Guerrero', 'Marín Socías', 'Diez Urzúa']
                
        # diputados presuntivos
        candidatos.loc[candidatos['Candidatos'].str.contains('Eduardo Errázuriz Larraín'), ['Electos','Electos_comp']] = [None, None]
        candidatos.loc[candidatos['Candidatos'].str.contains('Montané Urrejola'), ['Electos','Electos_comp']] = [None, None]
        candidatos.loc[candidatos['Candidatos'].str.contains('Olavarría Bravo'), ['Electos','Electos_comp']] = [None, None]
        candidatos.loc[candidatos['Candidatos'].str.contains('Germán Ignacio Riesco Errázuriz'), ['Electos','Electos_comp']] = [None, None]

        #correcciones
        # candidatos.loc[candidatos['Candidatos'].str.contains('Sabat Gozalo'), 'Partido'] = 'Partido Socialista'

        if not sum(candidatos['Candidatos'].str.contains('del Solar Urrutia')):
            candidatos.loc[len(candidatos.index),:] = 20,'','Domingo Antonio del Solar Urrutia','Partido Liberal Democrático','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Domingo_Antonio_Solar_Urrutia'

        
    if reemplazados:
        candidatos.loc[candidatos['Candidatos'].str.contains('|'.join(reemplazados)), 'Electos_comp'] = None

    if reemplazantes: 
        candidatos.loc[candidatos['Candidatos'].str.contains('|'.join(reemplazantes)), 'Electos'] = None

    candidatos[subdivrow] = candidatos[subdivrow].astype(int)  

    #no considera como duplicados los agregados para corregir 
    candidatos = candidatos.drop_duplicates(subset=['Candidatos'], keep="last")

    #verificar si están todos los diputados
    if True:
        count = candidatos[candidatos['Electos'] == '*'].groupby(['Distrito']).agg({'Electos':'count'})    
        if eleccion >= 1912:
            count['escanos'] = [4,2,2,3,3,4,2,3,3,7,13,4,3,3,3,2,2,3,2,2,2,3,2,2,2,2,2,2,1,3,3,4,2,2,4,4,2,2,2,2]

        # elif eleccion >= 1891:
        #     count['escanos'] = [4,7,2,7,3,12,5,6,4,3,5,3,4,3,5,9,2,4,6,10,5,3,3,3,1,18,5,5]
        
        count['diff'] = count['escanos'] -count['Electos']
        
        print('TOTAL : ', count['escanos'].sum())
    
        print('DESAJUSTES')
        print(count[count['diff'] != 0])
        print(candidatos[candidatos['Distrito'].isin(count[count['diff'] != 0].index)][['Distrito','Candidatos']].sort_values(['Candidatos']).sort_values(['Distrito']))
    
        print('')
        
        print('REEMPLAZOS')        
        print(candidatos[(candidatos['Electos_comp'] == '*') & (candidatos['Electos'] != '*')]['Candidatos'])

    return candidatos
