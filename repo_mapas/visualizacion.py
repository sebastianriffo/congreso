#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from modulos.division_politica import Division_electoral_shp
from modulos.resultados_elecciones import resultados_parlamentarias 
from modulos.pactos import leyendas_electorales
from modulos.mapa_folium import mapa_elecciones_folium

from pathlib import Path
from itertools import chain

#%%
def visualizacion(rep, eleccion):    
    """
    Crea un mapa en html para la elección y año solicitados. La información
    electoral y geometrías necesarias se encuentran en /input, siendo generadas
    en caso contrario.
        
    Parámetros
    ----------
    eleccion : int
        Año de la elección. Desde 1932 en adelante.
    rep : int
        Elección de diputados (0) o senadores (1).

    Entrega
    -------
    listas : dataframe
        Info electoral por Lista/Pacto, en cada subdivisión.
        indice = ['Distrito' o 'Circunscripción', 'Lista/Pacto']
        columnas = ['Candidaturas', 'Votos', 'Porcentaje', 'Electos']
        
    pp : dataframe 
        Info electoral por partido político, en cada subdivisión.    
        indice = ['Distrito' o 'Circunscripción', 'Lista/Pacto', 'Partido']     
        columnas = ['Candidaturas', 'Votos', 'Porcentaje', 'Electos']

    candidatos : dataframe 
        Info electoral por candidato, en cada subdivisión. Entre 1828 y 1969 
        se trata de los parlamentarios electos, mientras que desde 1973 en adelante
        es el listado de candidatos.
        indice = ['Distrito' o 'Circunscripción', 'Lista/Pacto', 'Partido']
        columnas = ['Candidatos', 'Votos', 'Porcentaje', 'Electos', 'Electos_comp', 'url']  

    electos : dataframe
        Candidatos electos en cada subdivisión. Notar que entre 1828 y 1969 es 
        idéntico a candidatos

    div_electoral : geodataframe
        Geometrías asociadas a la division electoral, según el año y elección.

    """
    
    root = Path.cwd()
    path_input = root / 'input'
    path_output = root / 'output'
            
    if eleccion not in list(chain({1828,1829}, range(1831,1925,3),{1925,1930,1932},range(1937,1974,4),range(1989,2022,4))):
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

    return listas, pp, candidatos, electos, div_electoral 