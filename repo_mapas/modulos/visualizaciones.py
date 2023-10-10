#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from division_politica import Division_electoral_shp
from resultados_elecciones import resultados_parlamentarias 

from pactos import leyendas_electorales
from mapa_folium import mapa_elecciones_folium

from pathlib import Path
from itertools import chain

#%%
# rep : diputados (0), senadores (1)
# eleccion : 1932, 1937, 1941,...,1973, 1989, 1993,..., 2021

root = Path.cwd().parents[0]
path_input = root / 'input'
path_output = root / 'output'

rep = 0
elecciones = [1989] #chain({1828,1829}, range(1831,1925,3),{1925,1930,1932},range(1937,1974,4),range(1989,2022,4)) 

#%%
for eleccion in elecciones: 
    print(eleccion)
        
    if eleccion not in list(chain({1932},range(1937,1974,4), range(1989,2022,4))):
        Exception()

    #%% Importar/descargar datos electorales    
    ## diferenciar entre electos, suplentes y reemplazantes (hasta 1891)

    print('Datos elección')
    
    if eleccion >= 1989:
        path_datos = path_input /''.join(['parlamentarias/1989-presente/',str(eleccion)])
    elif eleccion >= 1925:
        path_datos = path_input /''.join(['parlamentarias/1925-1973/',str(eleccion)])    
    elif eleccion >= 1891:
        path_datos = path_input /''.join(['parlamentarias/1891-1924/',str(eleccion)])
    else:
        path_datos = path_input /''.join(['parlamentarias/1828-1891/',str(eleccion)])
        
    path_datos.mkdir(parents=True, exist_ok=True)

    (listas,pp,candidatos) = resultados_parlamentarias(path_datos, eleccion, rep)        
    electos = candidatos[candidatos['Electos']=='*'][['Candidatos', 'Votos', 'Porcentaje','url']].fillna('')

    #%% Importar/descargar limites territoriales, dibujar mapas    
    print('Límites territoriales')
    div_electoral = Division_electoral_shp(path_input, eleccion, rep)

    print('Mapa')
    leyenda = leyendas_electorales(eleccion)        
        
    # resultados a nivel nacional
    path_mapas = path_output / 'legislaturas'
    path_mapas = path_mapas / ('1989-presente' if eleccion >= 1989 else '1925-1973')
        
    path_mapas.mkdir(parents=True, exist_ok=True)   
    mapa_elecciones_folium(path_mapas, eleccion, rep, listas, electos if eleccion <= 1969 else candidatos, div_electoral, leyenda)

    #%%    
    # if 'listas' in locals():
    #     del locals()['listas']