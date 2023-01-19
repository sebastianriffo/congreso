    #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Establece las divisiones electorales (distritos o circunscripciones) de Chile
desde 1989 en adelante. La función que lleva esto a cabo es *Division_electoral_shp*, 
la cual construye dichas divisiones gracias al shapefile de comunas presente 
en el sitio de la BCN.  

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

import requests, zipfile, io

def Division_electoral_shp(path_shapes, eleccion, rep):
    """
    genera un shapefile de distritos o circunscripciones correspondientes 
    a una elección parlamentaria, desde 1989 a la fecha.
    
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
    
    if eleccion == 2021:
        cols = [{0:'dist2021', 1:'circ2021'}[rep], 'codreg2021', 'geometry']
        vig = '2021'
    elif eleccion == 2017:
        cols = [{0:'dist2017', 1:'circ2017'}[rep], 'codreg2009', 'geometry']
        vig = '2017'        
    elif eleccion in {2009, 2013}:
        cols = [{0:'dist1989', 1:'circ2009'}[rep], 'codreg2009', 'geometry']
        vig = '2009'        
    elif eleccion in {1989, 1993, 1997, 2001, 2005}:
        cols = [{0:'dist1989', 1:'circ1989'}[rep], 'codreg1989', 'geometry']
        vig = '1989'        
    else:
        Exception()
    
    divCHILE = gpd.read_file(path_shapes.parents[3]/'input/shapes/source/comunasBCN/comunas.shp', encoding='utf-8')[cols]
    divCHILE = divCHILE.rename(columns={cols[0]:{0:'dis_elec', 1:'cir_sena'}[rep], cols[1]:'codregion'})
    
    # formar distritos/circunscripciones a partir de comunas        
    divCHILE['geometry'] = divCHILE.buffer(2.5)
    div_electoral = divCHILE.dissolve(by={0:'dis_elec',1:'cir_sena'}[rep])[['codregion','geometry']]    
    div_electoral['geometry'] = div_electoral['geometry'].simplify(125)
    
    # limpiar impurezas en las regiones de
    # 01. Tarapacá (dist 2, circ. 2)
    # 11. Aysén (1989: dist 59, circ 18; 2013: dist 27, circ 14)
    # 12. Magallanes (1989: dist 60, circ 19; 2013: dist 28, circ 15)
    imp = int(cols[0][4:])    
        
    for i in [1,11,12]:
        j = (i == 1)*(2*(rep == 0) +(1+(eleccion >= 2017))*(rep == 1)) + (i >= 11)*((27 +32*(imp <= 2009))*(rep == 0) +(14 +4*(imp <= 2009))*(rep == 1) +(i == 12))

        temp = gpd.GeoDataFrame(
            {'codregion':i,'geometry':[MultiPolygon([Polygon(list(P.exterior.coords)) for P in div_electoral.loc[j]['geometry'].geoms if not P.is_empty])]}
            ).set_crs('epsg:3857').set_index([[j]])        
        if i > 1 : temp['geometry'] = temp['geometry'].simplify(1250)
        
        div_electoral.loc[j] = temp.loc[j]    
    
    # nombres de distritos/circunscripciones
    div_electoral['nombre'] = div_electoral.index                    
    if rep == 0 or (rep == 1 and eleccion >= 2017):
        div_electoral['nombre'] = div_electoral['nombre'].apply(lambda x : 'Distrito '+str(x) if rep == 0 else str(x)+'ª Circunscripción')      
        
    else:
        div_electoral['nombre'] = div_electoral['nombre'].replace({1:"Tarapacá", 2:"Antofagasta", 3:"Atacama", 4:"Coquimbo", 
                                                                   5:"Valparaíso Cordillera", 6:"Valparaíso Costa", 7:"Santiago Poniente", 8:"Santiago Oriente", 9:"O'Higgins", 
                                                                   10:"Maule Norte", 11:"Maule Sur", 12:"Bío-Bío Costa", 13:"Bío-Bío Cordillera",
                                                                   14:"Araucanía Norte", 15:"Araucanía Sur", 16:"Los Ríos", 17:"Los Lagos", 18:"Aysén", 19:"Magallanes"}).astype(str)        
    div_electoral['nombre'] = div_electoral['nombre'].astype("string")
        
    div_electoral.to_file((path_shapes / (vig+{0:'_distritos.shp',1:'circunscripciones.shp'}[rep])))
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
        - 'circ1989', 'circ2017', 'circ2021' : circunscripciones,
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
