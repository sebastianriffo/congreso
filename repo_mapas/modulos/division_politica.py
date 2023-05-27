#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Establece las divisiones electorales (distritos o circunscripciones) de Chile
desde 1932 en adelante. La función que lleva esto a cabo es *Division_electoral_shp*, 
la cual construye dichas divisiones de dos maneras, dependiendo del período : 

- en 1932-1973, mediante un shapefile de los departamentos de Chile en 1973 
(elaboración  propia, aún en revisión), al cual se le agrega/modifica información 
usando la función *deptos1932_1973*.

- En 1989-2021, gracias al shapefile de comunas presente en el sitio de la BCN.  
Ya que este archivo no está al día, la función *comunas1989_presente* lo actualiza 
y luego agrega la información relativa a la creación de comunas, 
cambios en distritos, circunscripciones y regiones desde 1989 a la fecha. 
La división electoral usada en 1989-2018 se extrae de wikipedia por medio 
de la función *Division_electoral_1989_2018*.

""" 

import geopandas as gpd
import pandas as pd
from shapely.geometry import MultiPolygon, Polygon

from pathlib import Path
import re

import requests, zipfile, io

def Division_electoral_shp(path_input, eleccion, rep):
    """
    genera un shapefile de distritos o circunscripciones correspondientes 
    a una elección parlamentaria, desde 1941 a la fecha.
    
    Parámetros
    ----------
    path_shapes : PosixPath
        Directorio.    
    eleccion : int
        Año de la elección.
    rep : int
        Elección de diputados (0) o senadores (1).        

    Entrega
    -------
    div_electoral : geodataframe
        Geometrías asociadas a la division electoral, según el año y elección.
        
    """
    flatten_list = lambda test:[element for item in test for element in flatten_list(item)] if type(test) is list else [test]
    
    if eleccion >= 1989:
        if eleccion == 2021:
            cols, div_folder = [{0:'dist2021', 1:'circ2021'}[rep], 'codreg2021', 'geometry'], '2021'
        elif eleccion == 2017:
            cols, div_folder = [{0:'dist2017', 1:'circ2017'}[rep], 'codreg2009', 'geometry'], '2017'
        elif eleccion in {2009, 2013}:
            cols, div_folder = [{0:'dist1989', 1:'circ2009'}[rep], 'codreg2009', 'geometry'], '2009'
        elif eleccion in {1989, 1993, 1997, 2001, 2005}:
            cols, div_folder = [{0:'dist1989', 1:'circ1989'}[rep], 'codreg1989', 'geometry'], '1989'
            
        path_shapes = path_input / 'shapes/1989-presente/' 
            
    elif eleccion >= 1932:
        if eleccion in {1969,1973}:    
            cols, div_folder = [{0:'dist1969', 1:'circ1969'}[rep], 'geometry'], '1969'
        elif eleccion in {1961,1965}:    
            cols, div_folder = [{0:'dist1961', 1:'circ1941'}[rep], 'geometry'], '1961'
        elif eleccion in {1941,1945,1949,1953,1957}:    
            cols, div_folder = [{0:'dist1941', 1:'circ1941'}[rep], 'geometry'], '1941'
        elif eleccion == 1937:    
            cols, div_folder = [{0:'dist1937', 1:'circ1932'}[rep], 'geometry'], '1937' if rep == 0 else '1932' 
        elif eleccion == 1932:    
            cols, div_folder = [{0:'dist1932', 1:'circ1932'}[rep], 'geometry'], '1932' 
            
        path_shapes = path_input / 'shapes/1925-1973/'
    else:
        raise Exception('El año ingresado no corresponde a una elección, o bien la división electoral no se encuentra disponible')
        
    path_shapes = path_shapes / div_folder    
    path_shapes.mkdir(parents=True, exist_ok=True)

    # revisar si los polígonos ya fueron creados previamente
    if (path_shapes / (div_folder+{0:'_distritos.shp',1:'_circunscripciones.shp'}[rep]) ).is_file():
        div_electoral = gpd.read_file((path_shapes / (div_folder+{0:'_distritos.shp',1:'_circunscripciones.shp'}[rep])), encoding='latin-1')
        div_electoral = div_electoral.set_index([{0:'dis_elec',1:'cir_sena'}[rep]])
        
        return div_electoral

    ## GENERAR POLÍGONOS       
    if eleccion >= 1989:
        comunas1989_presente(path_input / 'shapes/source')
        
        divCHILE = gpd.read_file(path_shapes.parents[3]/'input/shapes/source/comunasBCN/comunas.shp', encoding='utf-8')[cols]
        divCHILE = divCHILE.rename(columns={cols[0]:{0:'dis_elec', 1:'cir_sena'}[rep], cols[1]:'codregion'})
        
        # formar distritos/circunscripciones a partir de comunas        
        divCHILE['geometry'] = divCHILE.buffer(2.5)
        div_electoral = divCHILE.dissolve(by={0:'dis_elec',1:'cir_sena'}[rep])[['codregion','geometry']]    
        div_electoral['geometry'] = div_electoral['geometry'].simplify(125)
        
        div_electoral['nombre'] = div_electoral.index                    
        
        if rep == 0:
            # nombres de distritos/circunscripciones
            regiones = {15:"Arica y Parinacota", 1:"Tarapacá", 2:"Antofagasta", 3:"Atacama", 4:"Coquimbo",
                        5:"Valparaíso", 13:"Santiago", 6:"O'Higgins", 7:"Maule", 8:"Bío-Bío", 16:"Ñuble",
                        9:"Araucanía", 14:"Los Ríos", 10:"Los Lagos", 11:"Aysén", 12:"Magallanes"} 
                        
            div_electoral['nombre'] = div_electoral.apply(lambda row : ''.join(['D', str(row['nombre']),' (',regiones[row['codregion']],')']), axis=1)            

        elif (rep == 1 and eleccion >= 2017):
            div_electoral['nombre'] = div_electoral['nombre'].replace({1:"Arica y Parinacota", 2:"Tarapacá", 3:"Antofagasta", 4:"Atacama", 5:"Coquimbo", 
                                                                       6:"Valparaíso", 7:"Santiago", 8:"O'Higgins", 9:"Maule", 10:"Bío-Bío",
                                                                       11:"Araucanía", 12:"Los Ríos", 13:"Los Lagos", 14:"Aysén", 15:"Magallanes", 16:"Ñuble"}).astype(str)            
        else:
            div_electoral['nombre'] = div_electoral['nombre'].replace({1:"Tarapacá", 2:"Antofagasta", 3:"Atacama", 4:"Coquimbo", 
                                                                       5:"Valparaíso Cordillera", 6:"Valparaíso Costa", 7:"Santiago Poniente", 8:"Santiago Oriente", 9:"O'Higgins", 
                                                                       10:"Maule Norte", 11:"Maule Sur", 12:"Bío-Bío Costa", 13:"Bío-Bío Cordillera",
                                                                       14:"Araucanía Norte", 15:"Araucanía Sur", 16:"Los Ríos", 17:"Los Lagos", 18:"Aysén", 19:"Magallanes"}).astype(str)

        #reducir tamaños de geometrías y limpiar impurezas
        r = div_electoral['nombre'].str.contains('Tarapacá|Aysén|Magallanes') 

        for j in r[r==True].index :
            if div_electoral.loc[j]['geometry'].geom_type == 'MultiPolygon':
                temp = gpd.GeoDataFrame({'codregion':div_electoral.loc[j]['codregion'],
                                         'nombre': div_electoral.loc[j]['nombre'],
                                         'geometry':[MultiPolygon([Polygon(list(P.exterior.coords)) for P in div_electoral.loc[j]['geometry'].geoms if not P.is_empty])]}
                                        ).set_crs('epsg:3857').set_index([[j]])        
    
                if (div_electoral['nombre'][j] != 'Tarapacá'): temp['geometry'] = temp['geometry'].simplify(1250)
                
                div_electoral.loc[j] = temp.loc[j]
                
    else:        
        deptos1932_1973(path_input / 'shapes/source')            
                
        # formar agrupaciones departamentales/senatoriales a partir de departamentos
        divCHILE = gpd.read_file(path_shapes.parents[3]/'input/shapes/source/1940-73_departamentos/div_1973.shp', encoding='utf-8')[cols]
        divCHILE = divCHILE.rename(columns={cols[0]:{0:'dis_elec', 1:'cir_sena'}[rep]})
                   
        div_electoral = divCHILE.dissolve(by={0:'dis_elec',1:'cir_sena'}[rep])[['geometry']]    

        # nombres de agrupaciones
        if rep == 0:
            provincias = flatten_list(['Tarapacá', 'Antofagasta', 'Atacama', 'Coquimbo', 'Aconcagua', 'Valparaíso', 
                                       ['Santiago-1', 'Santiago-2', 'Santiago-3', 'Santiago-4'], "O'Higgins", 'Colchagua', 'Curicó', 'Talca', 'Maule', 'Linares',
                                       ['Ñuble-1', 'Ñuble-2'], 'Concepción', 'Arauco', 'Bío-Bío', 'Malleco', 'Cautín', 
                                       'Valdivia', ['Osorno', 'Llanquihue', 'Chiloé', 'Aysén'] if eleccion >= 1969 else (['Osorno', 'Llanquihue y Aysén', 'Chiloé'] if eleccion >= 1941 else ['Llanquihue y Aysén', 'Chiloé']), 
                                       'Magallanes'])
        
            reg = list(range(1, len(provincias)-1))
            reg[7:7] = [71,72,73]
            reg.remove(7)        
        else:
            provincias = flatten_list(['Tarapacá y Antofagasta', 'Atacama y Coquimbo', 'Aconcagua y Valparaíso', 'Santiago', 
                                       "O'Higgins y Colchagua", 'Curicó, Talca, Maule y Linares', 'Ñuble, Concepción y Arauco', 'Bío-Bío, Malleco y Cautín',
                                       ['Valdivia, Osorno y Llanquihue', 'Chiloé, Aysén y Magallanes'] if eleccion >= 1969 else ('Valdivia, Osorno, Llanquihue, Chiloé, Aysén y Magallanes' if eleccion >= 1941 else 'Valdivia, Llanquihue, Chiloé, Aysén y Magallanes')
                                       ])           
            reg = list(range(1, len(provincias)+1))
        label = dict(zip(reg, provincias))
        
        div_electoral['nombre'] = div_electoral.index            
        div_electoral['nombre'] = div_electoral['nombre'].replace(label)

        #reducir tamaños de geometrías
        r = list(filter(re.compile('Aysén|Magallanes|Santiago-1|Santiago-2|Santiago-3').findall, provincias))
        
        div_electoral.loc[~div_electoral['nombre'].isin(r),'geometry'] = div_electoral[~div_electoral['nombre'].isin(r)]['geometry'].simplify(300)

        for prov in list(filter(re.compile('Aysén|Magallanes').findall, provincias)):
            div_electoral.loc[div_electoral['nombre'] == prov, 'geometry'] = div_electoral.loc[div_electoral['nombre'] == prov]['geometry'].simplify(1000)
                           
    div_electoral['nombre'] = div_electoral['nombre'].astype("string")
        
    div_electoral.to_file((path_shapes / (div_folder+{0:'_distritos.shp',1:'_circunscripciones.shp'}[rep])))
    
    return div_electoral

#%% MODIFICACIONES DESDE 1989
#%%
def comunas1989_presente(path_input_shapes):
    """
    Shapefile de las actuales comunas de Chile (345, no incluye a Antártica), 
    extraído de https://www.bcn.cl/siit/mapas_vectoriales/index_html (14/01/2023)
    con información adicional de regiones, circunscripciones y distritos 
    (y comunas si fuera el caso) a las que han pertenecido desde 1989.

    Parametros
    ----------
    path_input_shapes : PosixPath
        Directorio.
´
    Entrega
    -------
    divCHILE : geodataframe 
        Geometrías de comunas e información antes mencionada, presente en las columnas
        - 'Comuna' : listado por nombre,
        - 'codcom1989', 'codcom1997', 'codcom2005' : CUT (código único territorial),
        - 'dist1989', 'dist2017', 'dist2021' : distritos,
        - 'circ1989', 'circ2009', 'circ2017', 'circ2021' : circunscripciones,
        - 'codreg1989', 'codreg2009', 'codreg2021' : regiones.

    (El año indica la elección legislativa en la cual la division territorial 
    entró en vigor.) 
    
    """
    
    path_input_shapes = path_input_shapes/'comunasBCN'
    
    if not (path_input_shapes/'comunas.shp').is_file():
        path_input_shapes.mkdir(parents=True, exist_ok=True)
        
        # descargar limites : disponibles en https://www.bcn.cl/siit/mapas_vectoriales/index_html (13/06/2022)
        r = requests.get('https://www.bcn.cl/obtienearchivo?id=repositorio/10221/10396/2/Comunas.zip')
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(str(path_input_shapes))
 
    # 345 comunas al 2022 (no incluye Antártica)
    divCHILE = gpd.read_file(path_input_shapes/'comunas.shp', encoding='utf-8')   

    if 'dist1989' in divCHILE.columns.to_list():
        return divCHILE

    ## COMUNAS
    # codcom1989 : organización de 1989
    # codcom1997 : incorpora las comunas creadas entre 1994 y 1996 (Concón, Padre Hurtado, San Rafael, 
    #                  Chillán Viejo, Chiguayante, San Pedro de la Paz y Padre las Casas)
    # codcom2005 : incorpora las comunas creadas en 2004 (Alto Hospicio, Alto Biobío, Hualpén y Cholchol)
    divCHILE = divCHILE.set_index(['Comuna'])
    
    comunas1997 = {'Concón' : 'Viña del Mar',
                   'Padre Hurtado' : 'Peñaflor',
                   'San Rafael' : 'Pelarco',
                   'Chillán Viejo' : 'Chillán',
                   'Chiguayante' : 'Concepción',
                   'San Pedro de la Paz' : 'Concepción',
                   'Padre Las Casas' : 'Temuco'}
    
    comunas2005 = {'Alto Hospicio' : 'Iquique',
                   'Alto Biobío' : 'Santa Bárbara',
                   'Hualpén' : 'Talcahuano',
                   'Cholchol' : 'Nueva Imperial'}
    
    divCHILE['codcom1989'] = divCHILE['cod_comuna'].astype(int)
    divCHILE['codcom1997'] = divCHILE['cod_comuna'].astype(int)
    
    divCHILE.loc[comunas1997.keys(),'codcom1989'] = divCHILE.loc[comunas1997.values(),'cod_comuna'].values
    divCHILE.loc[comunas2005.keys(),'codcom1989'] = divCHILE.loc[comunas2005.values(),'cod_comuna'].values
    divCHILE.loc[comunas2005.keys(),'codcom1997'] = divCHILE.loc[comunas2005.values(),'cod_comuna'].values
    
    divCHILE.rename(columns={'cod_comuna':'codcom2005'}, inplace=True)    
    divCHILE = divCHILE.reset_index()
    
    ## DISTRITOS Y CIRCUNSCRIPCIONES
    # dist1989 : 60 distritos, ley 18700 de 1988
    # dist2017 : 28 distritos, reforma electoral de 2015 
    # dist2021 : comunas de Cabrero y Yumbel cambian de distrito (19 al 21)     
    #
    # circ1989 : 19 circunscripciones, ley 18700 de 1988
    # circ2009 : el distrito 55 cambia de circunscripción (16 a 17)    
    # circ2017 : 15 circunscripciones, reforma electoral de 2015 
    # circ2021 : nueva circunscripción (16) por la creación de la región de Ñuble

    # webscraping para el período 1989-2018 (dist1989, circ1989, circ2009)    
    divCHILE_binominal = Division_electoral_1989_2018()
    divCHILE = divCHILE.merge(divCHILE_binominal, on='Comuna')    

    # el distrito 21 no está actualizado
    divCHILE['dist2021'] = divCHILE['dis_elec'].astype(int) 
    divCHILE.loc[divCHILE['Comuna'] == 'Cabrero','dist2021'] = 21
    divCHILE.loc[divCHILE['Comuna'] == 'Yumbel','dist2021'] = 21    

    divCHILE.rename(columns={'dis_elec':'dist2017'}, inplace=True)    

    divCHILE['circ2017'] = divCHILE['cir_sena'].astype(int)    

    # la circunscripción 16 no está actualizada 
    divCHILE.loc[divCHILE['codregion'] == 16,'cir_sena'] = 16

    divCHILE.rename(columns={'cir_sena':'circ2021'}, inplace=True)
         
    ## REGIONES
    # codreg1989 : regiones originales de la Constitución de 1980 
    # codreg2009 : nuevas regiones de los Ríos (14) y Arica y Parinacota (15) en 2007
    # codreg2021 : nueva región de Ñuble, en 2018
    
    divCHILE['codreg1989'] = divCHILE['codregion'].astype(int)
    divCHILE['codreg2009'] = divCHILE['codregion'].astype(int)

    divCHILE.loc[divCHILE['codreg1989'] == 14, 'codreg1989'] = 10
    divCHILE.loc[divCHILE['codreg1989'] == 15, 'codreg1989'] = 1
    divCHILE.loc[divCHILE['codreg1989'] == 16, 'codreg1989'] = 8    

    divCHILE.loc[divCHILE['codreg2009'] == 16, 'codreg2009'] = 8
        
    divCHILE.rename(columns={'codregion':'codreg2021'}, inplace=True) 
        
    ## columnas finales
    divCHILE = divCHILE.drop(columns=['Region','Provincia'])
    divCHILE = divCHILE.reindex(['Comuna',
                                 'codcom1989', 'codcom1997', 'codcom2005',
                                 'dist1989', 'dist2017', 'dist2021',
                                 'circ1989', 'circ2009', 'circ2017', 'circ2021',
                                 'codreg1989','codreg2009','codreg2021',
                                 'objectid', 'shape_leng','st_area_sh', 'st_length_', 'geometry'],axis=1)
    
    divCHILE.to_file(path_input_shapes/'comunas.shp')
    
    return divCHILE

#%%
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
pd.options.mode.chained_assignment = None

def Division_electoral_1989_2018():
    """
    Webscraping de la división territorial de Chile en 1989-2018, desde  
    https://es.wikipedia.org/wiki/División_electoral_de_Chile
    
    Entrega
    -------
    divCHILE1989 : dataframe
        Comunas actuales (2023) y sus respectivos distritos y circunscripciones
        en el período 1989-2018.

    """
    ## WEBSCRAPING
    # iniciar selenium en Chrome   
    chrome_service = Service('/usr/bin/chromedriver')
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--headless') 
    
    driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
    driver.get('https://es.wikipedia.org/wiki/Divisi%C3%B3n_electoral_de_Chile')
    
    # extraer 
    html = driver.page_source
    soup = BeautifulSoup(html,'html.parser')
            
    table_html = soup.find_all('table', class_="wikitable")        

    # tabla 2 : «Antiguas divisiones electorales, 1989-2018»
    rows_tr = table_html[2].tbody.find_all('tr')
        
    output_tbody = []
    aux = []
    
    for row in rows_tr[1:]:
        cols = row.find_all('td')
        cols[0:0] = row.find_all('th')            
        cols = [item.text.strip() for item in cols]        
        cols[0:0] = aux[0:4-len(cols)]
            
        output_tbody.append(cols[1:]) 

        aux = cols
    
    ## CREAR y FORMATEAR TABLA
    divCHILE = pd.DataFrame.from_records(output_tbody, columns=['circ2009','dist1989','Comuna'])
    
    divCHILE['Comuna'] = divCHILE['Comuna'].replace({'La Calera':'Calera', 'Coínco':'Coinco', 
                                                             'Ránquil':'Ranquil', 'Los Álamos':'Los Alamos',
                                                             'Los Ángeles':'Los Angeles'})
    divCHILE['dist1989'] = divCHILE['dist1989'].astype(int)
        
    divCHILE['circ2009'] = divCHILE['circ2009'].replace(r'[^IVX]', '', regex=True)
    divCHILE['circ2009'] = divCHILE['circ2009'].replace({'VV':'V', 'VIV':'VI', '':'I'})
    divCHILE['circ2009'] = divCHILE['circ2009'].replace({'I':1, 'II':2, 'III':3, 'IV':4, 'V':5,
                                                                 'VI':6, 'VII':7, 'VIII':8, 'IX':9, 'X':10,
                                                                 'XI':11, 'XII':12, 'XIII':13, 'XIV':14, 'XV':15,
                                                                 'XVI':16, 'XVII':17, 'XVIII':18, 'XIX':19})

    divCHILE['circ1989'] = divCHILE['circ2009']
    divCHILE.loc[divCHILE['dist1989'] == 55,'circ1989'] = 16 

    divCHILE = divCHILE.reindex(['Comuna','dist1989','circ1989','circ2009'],axis=1)
    return divCHILE

#%% MODIFICACIONES ENTRE 1941-1973
#%%
def deptos1932_1973(path_input_shapes):
    """
    Agrega información a un shapefile de los departamentos de Chile en 1973 
    (elaboración propia), relativa a departamentos, agrupaciones departamentales
    y senatoriales a las que estos pertenecieron en el período 1932-1973.

    El archivo original cuenta con dos columnas : 'cod','depto1973' y 'dist1973'.

    Parametros
    ----------
    path_input_shapes : PosixPath
        Directorio.
´
    Entrega
    -------
    divCHILE : geodataframe 
        Geometrías de comunas e información antes mencionada, presente en las columnas
        - 'cod' : codigo de origen para cada seccion de departamento,
        - 'depto1973', 'depto1969', 'depto1965', 'depto1961', 'depto1949', 'depto1941', 'depto1937', 'depto1932' : departamentos (actuales provincias)
        - 'dist1969', 'dist1941', 'dist1937', 'dist1932' : agrupaciones departamentales (actuales distritos),
        - 'circ1969', 'circ1941', 'circ1937', 'circ1932' : agrupaciones senatoriales (actuales circunscripciones).

    (El año indica la elección legislativa en la cual la division territorial 
    entró en vigor.) 
    
    """
     
    path_input_shapes = path_input_shapes/'1940-73_departamentos'
    
    if (path_input_shapes/'div_1973.shp').is_file():
        divCHILE = gpd.read_file(path_input_shapes/'div_1973.shp', encoding='utf-8')   
    else:
        raise Exception('div_1973.shp no existe')

    if 'depto1932' in divCHILE.columns.to_list():
        return divCHILE

    ## DEPARTAMENTOS
    # depto1973 : organización base de 1973. Incorpora Baker y General Carrera (1970, ex Chile Chico), Cardenal Caro (1973, parte de Colchagua). 
    # depto1969 : Isla de Pascua (1966, parte de Valparaíso), Panguipulli (1968, parte de Valdivia)
    # depto1965 : PAC (1963, parte de Santiago)   
    # depto1961 : Puente Alto (1958, parte de Santiago); Aysen, Coyhaique y Chile Chico (1959, ex Aysen).
    #             Palena (1959), parte de Quinchao, pasa de Chiloe a Aysen. Islas Cuptana y Transito pasan de Aysen a Chiloe (Castro).
    # depto1949 : Curacautin (1945, parte de Malleco)
    # depto1941 : Combarbalá (parte de Ovalle), río Negro (1940, parte de Osorno)
    # depto1937 : Coquimbo (parte de La Serena), San Bernardo (parte de Santiago-2), Curepto (parte de Mataquito). 
    #             Talcahuano (parte de Concepción), Lebu (parte de Arauco), Pitrufquen (parte de Villarrica), 
    #             Río Bueno (La Unión); Pto Varas, Maullin, Calbuco, Quinchao (llanquihue)
    # depto1932 : -
    
    divCHILE['depto1969'] = divCHILE['depto1973']
    divCHILE['depto1969'] = divCHILE['depto1969'].replace({"Baker":"Chile Chico", "General Carrera":"Chile Chico", "Cardenal Caro":"Colchagua"})

    divCHILE['depto1965'] = divCHILE['depto1969']    
    divCHILE['depto1965'] = divCHILE['depto1965'].replace({"Isla de Pascua":"Valparaiso", "Panguipulli":"Valdivia"})

    divCHILE['depto1961'] = divCHILE['depto1965']    
    divCHILE['depto1961'] = divCHILE['depto1961'].replace({"Pedro Aguirre Cerda":"Santiago"})

    divCHILE['depto1949'] = divCHILE['depto1961']
    divCHILE['depto1949'] = divCHILE['depto1949'].replace({"Puente Alto":"Santiago", "Coyhaique":"Aysen", "Chile Chico":"Aysen"})

    divCHILE.loc[divCHILE['cod'] == 91,'depto1949'] = 'Quinchao'
    divCHILE.loc[divCHILE['cod'] == 93,'depto1949'] = 'Aysen'    
    divCHILE.loc[divCHILE['cod'] == 98,'depto1949'] = None
    divCHILE.loc[divCHILE['cod'] == 99,'depto1949'] = None    

    divCHILE['depto1941'] = divCHILE['depto1949']
    divCHILE['depto1941'] = divCHILE['depto1941'].replace({"Curacautin":"Victoria"})    

    divCHILE['depto1937'] = divCHILE['depto1941']  
    divCHILE['depto1937'] = divCHILE['depto1937'].replace({"Combarbala":"Ovalle"})    
    divCHILE['depto1937'] = divCHILE['depto1937'].replace({"Talagante":"Santiago-2"})     
    divCHILE['depto1937'] = divCHILE['depto1937'].replace({"Nacimiento":"Mulchén"})         
    divCHILE['depto1937'] = divCHILE['depto1937'].replace({"Collipulli":"Victoria"})    
    divCHILE['depto1937'] = divCHILE['depto1937'].replace({"Río Negro":"Osorno"})    

    divCHILE['depto1932'] = divCHILE['depto1937']  
    divCHILE['depto1932'] = divCHILE['depto1932'].replace({"Coquimbo":"La Serena"})    
    divCHILE['depto1932'] = divCHILE['depto1932'].replace({"San Bernardo":"Santiago-2"})        
    divCHILE['depto1932'] = divCHILE['depto1932'].replace({"San Vicente":"Cachapoal"})    
    divCHILE['depto1932'] = divCHILE['depto1932'].replace({"Curepto":"Mataquito"})    
    divCHILE['depto1932'] = divCHILE['depto1932'].replace({"Talcahuano":"Concepción"})    
    divCHILE['depto1932'] = divCHILE['depto1932'].replace({"Coronel":"Yumbel"})    
    divCHILE['depto1932'] = divCHILE['depto1932'].replace({"Lebu":"Arauco"})        
    divCHILE['depto1932'] = divCHILE['depto1932'].replace({"Pitrufquen":"Villarrica"})    
    divCHILE['depto1932'] = divCHILE['depto1932'].replace({"Río Bueno":"La Union"})    
    divCHILE['depto1932'] = divCHILE['depto1932'].replace({"Puerto Varas":"Llanquihue"})        
    divCHILE['depto1932'] = divCHILE['depto1932'].replace({"Maullin":"Llanquihue"})            
    divCHILE['depto1932'] = divCHILE['depto1932'].replace({"Calbuco":"Llanquihue"})        
    divCHILE['depto1932'] = divCHILE['depto1932'].replace({"Quinchao":"Llanquihue"})        
    
    ## DISTRITOS (agrupaciones departamentales) Y CIRCUNSCRIPCIONES (agrupaciones senatoriales)
    # dist1969 : se crea la AD 26 (Aysen, Coyhaique y Chile Chico, antes parte de Llanquihue)
    # dist1961 : considera los cambios en chiloé y aysén
    # dist1941 : se crea la AD 23 de Osorno y Río Bueno
    # dist1937 : San Bernardo pasa de Santiago-3 a Santiago-4, Curepto de Curicó a Talca, Quinchao de Llanquihue a Chiloé
    # dist1932 : - 
    
    dist = {"Tarapaca":1, "Antofagasta":2, "Atacama":3, "Coquimbo":4, "Aconcagua":5, "Valparaiso":6,
            "Santiago-1":71, "Santiago-2":72, "Santiago-3":73, "Santiago-4":8, 
            "O'Higgins":9, "Colchagua":10, "Curico":11, "Talca":12, "Maule":13, "Linares":14, 
            "Nuble-1":15, "Nuble-2":16, "Concepcion":17, "Arauco":18, "Biobio":19, "Malleco":20, "Cautin":21,
            "Valdivia":22, "Osorno":23, "Llanquihue":24, "Chiloe":25, "Aysen":26, "Magallanes":27}

    divCHILE['dist1969'] = divCHILE['dist1973']
    divCHILE['dist1969'] = divCHILE['dist1969'].replace(dist)
    divCHILE['dist1969'] = divCHILE['dist1969'].astype(int)    

    divCHILE['dist1961'] = divCHILE['dist1969']
    divCHILE.loc[divCHILE['dist1961'] == 26,'dist1961'] = 24            
    divCHILE.loc[divCHILE['dist1961'] == 27,'dist1961'] = 26    
                
    divCHILE['dist1941'] = divCHILE['dist1961']    

    # palena (91), islas cuptana y transito (93)
    divCHILE.loc[divCHILE['cod'] == 91,'dist1941'] = 25 
    divCHILE.loc[divCHILE['cod'] == 93,'dist1941'] = 24

    divCHILE['dist1941'] = divCHILE['dist1941'].astype(int)    

    ## los mapas de 1932 y 1937 son referenciales, hechos a partir de la info levantada en 1941. Se omiten cambios de límites entre departamentos.
    # angol (68) pasa de malleco a biobio, lautaro (73) de cautin a malleco
    divCHILE['dist1937'] = divCHILE['dist1941']
    divCHILE.loc[divCHILE['cod'] == 68,'dist1937'] = 19    
    divCHILE.loc[divCHILE['cod'] == 73,'dist1937'] = 20    
    
    divCHILE.loc[divCHILE['dist1937'] == 23,'dist1937'] = 22
    divCHILE.loc[divCHILE['dist1937'] == 24,'dist1937'] = 23
    divCHILE.loc[divCHILE['dist1937'] == 25,'dist1937'] = 24
    divCHILE.loc[divCHILE['dist1937'] == 26,'dist1937'] = 25

    divCHILE['dist1937'] = divCHILE['dist1937'].astype(int)    

    # San Bernardo (31) pasa de Santiago-3 a Santiago-4, Curepto (43) de Curicó a Talca, Quinchao (90, 91, 92)de Llanquihue a Chiloé
    divCHILE['dist1932'] = divCHILE['dist1937']
    divCHILE.loc[divCHILE['cod'] == 31,'dist1932'] = 72
    divCHILE.loc[divCHILE['cod'] == 43,'dist1932'] = 11
    divCHILE.loc[divCHILE['cod'] == 90,'dist1932'] = 23  
    divCHILE.loc[divCHILE['cod'] == 91,'dist1932'] = 23  
    divCHILE.loc[divCHILE['cod'] == 92,'dist1932'] = 23  
    
    divCHILE['dist1932'] = divCHILE['dist1932'].astype(int)    
    
    # circ1969 : se crea la AS 10 (Chiloe, Aysen y Magallanes, antes parte de la 9)
    # circ1941 : revisar
    # circ1932 : revisar
    circ = {"Tarapaca":1, "Antofagasta":1, "Atacama":2, "Coquimbo":2, "Aconcagua":3, "Valparaiso":3,
            "Santiago-1":4, "Santiago-2":4, "Santiago-3":4, "Santiago-4":4, 
            "O'Higgins":5, "Colchagua":5, "Curico":6, "Talca":6, "Maule":6, "Linares":6, 
            "Nuble-1":7, "Nuble-2":7, "Concepcion":7, "Arauco":7, "Biobio":8, "Malleco":8, "Cautin":8,
            "Valdivia":9, "Osorno":9, "Llanquihue":9, "Chiloe":10, "Aysen":10, "Magallanes":10}

    divCHILE['circ1969'] = divCHILE['dist1973']
    divCHILE['circ1969'] = divCHILE['circ1969'].replace(circ)
    divCHILE['circ1969'] = divCHILE['circ1969'].astype(int)    
    
    divCHILE['circ1941'] = divCHILE['circ1969']    
    divCHILE.loc[divCHILE['circ1941'] == 10,'circ1941'] = 9
    divCHILE['circ1941'] = divCHILE['circ1941'].astype(int)    
 
    divCHILE['circ1932'] = divCHILE['circ1941']    
    divCHILE['circ1932'] = divCHILE['circ1932'].astype(int)        
    
    ## columnas finales
    divCHILE = divCHILE.drop(columns=['dist1973'])    
    divCHILE = divCHILE.reindex(['cod',
                                 'depto1973', 'depto1969', 'depto1965', 'depto1961', 'depto1949', 'depto1941', 'depto1937', 'depto1932',
                                 'dist1969', 'dist1961', 'dist1941', 'dist1937', 'dist1932',
                                 'circ1969', 'circ1941', 'circ1932',
                                 'geometry'],axis=1)
    
    divCHILE.to_file(path_input_shapes/'div_1973.shp')
    
    return divCHILE