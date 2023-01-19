#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from division_politica import comunas1989_presente, Division_electoral_shp
from resultados_elecciones import resultados_parlamentarias, Senado1989_presente

from pactos import leyendas_electorales
from mapa_folium import mapa_elecciones_folium
from resultados_miscelaneo import biografiasBCN

import geopandas as gpd
import pandas as pd
from pathlib import Path
from ast import literal_eval
import re
from itertools import chain

#%%
# rep : diputados (0), senadores (1)
# eleccion : 1941,...,1973, 1989,..., 2021

root = Path.cwd().parents[0]
path_input = root / 'input'
path_output = root / 'output'

rep = 0
elecciones = list(chain(range(1941,1974,4), range(1989,2022,4)))

#%%
for eleccion in elecciones: 
    print(eleccion)

    if rep == 0:
        if eleccion >= 1989:
            cargos = 120 +35*(eleccion >= 2017)
        elif eleccion >= 1941:
            cargos = 147 +3*(eleccion >= 1969)
        # 132 desde 1925, 
        # 133 desde 1930,
        # 142 desde 1932, 
        # 146 desde 1937, 
        else: 
            Exception()       
    else:
        if eleccion == 2021:
            cargos = 27
        elif eleccion == 2017:
            cargos = 23
        elif eleccion in {1997, 2005, 2013}:
            cargos = 20
        elif eleccion in {1993, 2001, 2009}:
            cargos = 18
        elif eleccion == 1989:
            cargos = 38
        else:
            Exception()       
        
    #%% Importar/descargar limites territoriales    
    print('Límites territoriales')
    
    if eleccion >= 1989:
        comunas1989_presente(path_input / 'shapes/source')
    
    # directorios por año
    if eleccion == 2021:
        path_shapes = path_input / 'shapes/1989-presente/2021/'
        vig = '2021'
    elif eleccion == 2017: 
        path_shapes = path_input / 'shapes/1989-presente/2017/'
        vig = '2017'
    elif eleccion in {2009, 2013}:
        path_shapes = path_input / 'shapes/1989-presente/2009/'
        vig = '2009'
    elif eleccion in {1989, 1993, 1997, 2001, 2005}: 
        path_shapes = path_input / 'shapes/1989-presente/1989/'
        vig = '1989'
    elif eleccion in {1969,1973}:    
        path_shapes = path_input / 'shapes/1925-1973/1969/'
        vig = '1969'
    elif eleccion in {1961, 1965}:
        path_shapes = path_input / 'shapes/1925-1973/1961/'
        vig = '1961'        
    elif eleccion in {1941,1945,1949,1953,1957}:
        path_shapes = path_input / 'shapes/1925-1973/1941/'
        vig = '1941'
    else:
        Exception()
    
    path_shapes.mkdir(parents=True, exist_ok=True)
    
    if (path_shapes / (vig+{0:'_distritos.shp',1:'_circunscripciones.shp'}[rep]) ).is_file():
        div_electoral = gpd.read_file((path_shapes / (vig+{0:'_distritos.shp',1:'_circunscripciones.shp'}[rep])), encoding='latin-1')
        div_electoral = div_electoral.set_index([{0:'dis_elec',1:'cir_sena'}[rep]])
    else:    
        div_electoral = Division_electoral_shp(path_shapes, eleccion, rep)
    
    #%% Importar/descargar datos electorales    
    print('Datos elección')
    
    if eleccion >= 1989:
        path_datos = path_input /''.join(['parlamentarias/1989-presente/',str(eleccion)])
    else:
        path_datos = path_input /''.join(['parlamentarias/1925-1973/',str(eleccion)])    
    path_datos.mkdir(parents=True, exist_ok=True)
    
    datos_filenames = sorted(path_datos.glob(''.join(['*',{0:'Distrito',1:'Circunscripcion'}[rep],'*'])))
    
    if datos_filenames:
        for file in datos_filenames: 
            filename = re.split('_|.csv',file.as_posix())[-2]
            
            locals()[filename] = pd.read_csv(file).fillna('')
            
            if 'listas' in filename:
                cols = [{0:'Distrito',1:'Circunscripción'}[rep], 'Lista/Pacto']
            elif 'pp' in filename:         
                cols = [{0:'Distrito',1:'Circunscripción'}[rep], 'Lista/Pacto', 'Partido']
            else:
                cols = [{0:'Distrito',1:'Circunscripción'}[rep], 'Lista/Pacto', 'Partido']
                locals()[filename]['Candidatos'] = locals()[filename]['Candidatos'].apply(lambda x : literal_eval(str(x)))
            
            locals()[filename] = locals()[filename].set_index(cols)
            
        if 'listas' not in locals():
            listas = None
    else:   
        (listas,pp,candidatos) = resultados_parlamentarias(path_datos, eleccion, rep)
        
        prefix_filename = ''.join(['Eleccion',str(eleccion),'_',{0:'Distrito',1:'Circunscripcion'}[rep]])    
        if eleccion >= 1973:

            #añadir biografías             
            print('Datos BCN')            
            if sum(candidatos['Electos'] == '*') == cargos:
                biografiasBCN(eleccion, candidatos)           

                # Senadores electos en el período anterior (+designados y vitalicios en 1990-2006)
                if rep == 1 and eleccion >= 1989:
                    print('Senadores en ejercicio')
                    candidatos = Senado1989_presente(path_datos, candidatos, eleccion)
                    candidatos.to_csv(path_datos/(prefix_filename+'_candidatos.csv'))

        electos = candidatos[candidatos['Electos'] == '*']                    
        electos.to_csv(path_datos/(prefix_filename+'_electos.csv'))

    electos = electos[electos['Electos']=='*'][['Candidatos', 'Votos', 'Porcentaje','url']].fillna('')
                                     
    #%% Dibujar mapas por distritos o circunscripciones    
    print('Mapa')
        
    leyenda = leyendas_electorales(eleccion)        
        
    # resultados a nivel nacional
    path_mapas = path_output / 'legislaturas'
    path_mapas = path_mapas / ('1989-presente' if eleccion >= 1989 else '1925-1973')
        
    path_mapas.mkdir(parents=True, exist_ok=True)
    
    mapa_elecciones_folium(path_mapas, eleccion, rep, listas, electos if eleccion <= 1969 else candidatos, div_electoral, leyenda)
    
    #%%
    if 'listas' in locals():
        del locals()['listas']