#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrae/construye la información electoral usando diversas fuentes, mediante 
la función *resultados_parlamentarias*. La información varía según la elección, 
por lo que se observan dos períodos : 

- 1973-2021, con resultados detallados a nivel nacional, extraídos del SERVEL (1989-)
y wikipedia (1973). En el caso de la elección de senadores, la función 
*parlamentarios1973_presente* armoniza la información entre una elección y la anterior, 
para visualizar la conformación de dicha cámara en el mapa final. Igualmente, 
crea un listado de parlamentarios electos.

- 1932-1969, correspondiente a la conformación de la Cámara de Diputados y el Senado. 
Diversas informaciones relativas a los parlamentarios son corregidas mediante 
*parlamentarios1925_1969*. En caso de tener resultados a nivel provincial, 
estos se agregan usando la función *resultados1925_1969*.

"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from bs4 import BeautifulSoup
import time 
import pandas as pd
pd.options.mode.chained_assignment = None

from pathlib import Path
import re
from operator import itemgetter
from ast import literal_eval

from pactos import pactos_electorales, siglas_partidos
from resultados_miscelaneo import nombres_formato, biografiasBCN

from resultados.parlamentarios1973_presente import parlamentarios1973_presente
from resultados.parlamentarios1925_1969 import parlamentarios1925_1969
from resultados.resultados1925_1969 import resultados1925_1969

def resultados_parlamentarias(path_datos, eleccion, rep, subdiv=None):    
    """
    Webscraping de las elecciones de diputados y/o senadores en 1932-2021, 
    desde los sitios web del SERVEL histórico (1989-2021), wikipedia (1973) y 
    BCN (1932-1969).
    
    Parámetros
    ----------
    path_datos : PosixPath
        Directorio.
    eleccion : int
        Año de la elección.
    rep : int
        Elección de diputados (0) o senadores (1).
    subdiv : list[int], opcional
        Lista numerada de distritos o circunscripciones. Toma por defecto los del año correspondiente.        

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
        Info electoral por candidato, en cada subdivisión. Entre 1941 y 1969 
        se trata de los parlamentarios electos, mientras que desde 1973 en adelante
        es el listado de candidatos.
        indice = ['Distrito' o 'Circunscripción', 'Lista/Pacto', 'Partido']
        columnas = ['Candidatos', 'Votos', 'Porcentaje', 'Electos', 'Electos_comp', 'url']  
        
    (Notar que 'Lista/Pacto' sigue un orden categórico.)
    
    """        

    if not eleccion in {1932}.union(set(range(1937,1977,4)).union(set(range(1989,2025,4)))):
        raise Exception('El año ingresado no corresponde a una elección, o bien esta no se encuentra disponible')
        
    ## Distritos o circunscripciones por elección, a partir de 1989
    if eleccion >= 1989:
        if rep == 0:        
            subdivision = list(range(1,28+32*(eleccion <= 2013)+1))
        else:
            if eleccion == 2021:
                subdivision = [3,5,7,8,10,12,13,15,16]        
            elif eleccion == 2017:
                subdivision = [1,2,4,6,9,11,14]
            elif eleccion in {1997, 2005, 2013}:
                subdivision = [2,4,7,8,9,12,13,16,17,19]
            elif eleccion in {1993, 2001, 2009}:
                subdivision = [1,3,5,6,10,11,14,15,18]    
            else:
                subdivision = list(range(1,20))

    if subdiv != None:
          subdivision = list(set(subdiv).intersection(set(subdivision)))
            
          if not subdivision:
              raise Exception('La numeración de distritos o circunscripciones ingresadas no corresponde')
            
    subdivrow = {0:'Distrito',1:'Circunscripción'}[rep]
    
    flag_reload = False
    
#%% CANDIDATOS
    if subdiv == None: 
        datos_filenames = sorted(path_datos.glob(''.join(['*',{0:'Distrito',1:'Circunscripcion'}[rep],'*'])))
        
    if datos_filenames:
        flag_reload = True
        
        for file in datos_filenames: 
            filename = re.split('_|.csv',file.as_posix())[-2]
            
            if ('electos' in filename and eleccion <= 1969) or ('candidatos' in filename and eleccion >= 1973):
                cols = [subdivrow,'Lista/Pacto','Candidatos', 'Partido', 'Votos', 'Porcentaje', 'Electos', 'Electos_comp', 'url'] 

                candidatos = pd.read_csv(file)
                candidatos = candidatos[cols]
                candidatos = candidatos.fillna('')                  
                
                candidatos['Candidatos'] = candidatos['Candidatos'].apply(lambda x : literal_eval(str(x))).apply(' '.join)
            
            elif ('pp' in filename):
                pp = pd.read_csv(file)
            elif ('listas' in filename):
                listas = pp = pd.read_csv(file)
    else:                        
        # WEBSCRAPING
        print('webscraping')
        
        # iniciar selenium en Chrome   
        chrome_service = Service('/usr/bin/chromedriver')
        chrome_options = Options()
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument('--headless') 
        
        driver = webdriver.Chrome(options=chrome_options, service=chrome_service)

        if eleccion >= 2013:            
            if eleccion == 2021:
                website = '234'*(rep == 0) +'233'*(rep == 1)
            elif eleccion == 2017:
                website = '215'*(rep == 0) +'220'*(rep == 1)
            else:
                website = '4'*(rep == 0) +'3'*(rep == 1)
            
            url = ''.join(['https://historico.servel.cl/servel/app/index.php?r=EleccionesGenerico&id=',website]) 
            
        elif eleccion >= 1989:            
            url = ''.join(['https://historico.servel.cl/SitioHistorico/index',str(eleccion),{0:'_dipu.htm', 1:'_sena.htm'}[rep]])
        elif eleccion == 1973:
            url = 'https://es.wikipedia.org/wiki/Anexo:Resultados_de_las_elecciones_parlamentarias_de_Chile_de_1973'
        elif eleccion >= 1925:
            url = ''.join(['https://www.bcn.cl/historiapolitica/corporaciones/periodo_detalle?inicio=',
                           str(eleccion),'-05-21' if (eleccion >= 1937 or eleccion == 1930) else ('-12-19' if eleccion == 1932 else '-12-23'),'&fin=',
                           str(eleccion+4) if (eleccion >= 1937) else (str(eleccion+2) if eleccion == 1930 else str(eleccion+5)),
                           '-05-20' if (eleccion != 1930) else '-06-06',                           
                           '&periodo=1925-1973&cam=','Diputados' if rep == 0 else 'Senado'])   

        elif eleccion >= 1891: 
            url = ''.join(['https://www.bcn.cl/historiapolitica/corporaciones/periodo_detalle?inicio=',
                           str(eleccion),'-06-01' if (eleccion >= 1894) else '-12-26','&fin=',
                           str(eleccion+3) if eleccion < 1924 else '1924',
                           '-05-31' if eleccion < 1924 else '-09-11',                  
                           '&periodo=1891-1925&cam=','Diputados' if rep == 0 else 'Senado'])               

        driver.get(url)
                
        # extraer 
        html = driver.page_source
        soup = BeautifulSoup(html,'html.parser')
                
        output_tbody = []

        if eleccion >= 1989:
            header = [subdivrow,'Lista/Pacto','Candidatos', 'Partido', 'Votos', 'Porcentaje', 'Electos']

            # sitio «moderno» del servel histórico            
            if 2013 <= eleccion <= 2021: 
                # seleccionar subdivisión
                element_id = {0:'selDistrito',1:'selCircunscripcionSenatorial'}[rep]   
                label = [{0:'Distrito ',1:'Circunscripción Senatorial '}[rep] +str(i) for i in subdivision]
                
                select = Select(driver.find_element(By.ID,element_id))
                time.sleep(1)              
                
                output_tbody = []
                
                for i in range(0,len(label)):
                    select.select_by_visible_text(label[i])    
                    time.sleep(2)
                    
                    # web scraping via BS4    
                    html = driver.page_source
                    soup = BeautifulSoup(html,'html.parser')
                            
                    table_html = soup.find('table', class_='table pactopais table-hover table-striped')    
                    rows_tr = table_html.find_all('tr')
                
                    for row in rows_tr[1:]: #rows_tr[1:-5]:                        
                        if row in rows_tr[1:-5]:
                            cols = row.find_all('td')
                        elif row in rows_tr[-4:]:
                            cols = row.find_all('th')
                        else:
                            continue
                          
                        cols = [item.text.strip() for item in cols]

                        if cols: 
                            cols[1] = cols[1].replace('IND-','') #corregir de 2017 en adelante (?)
                            cols[2] = cols[2].replace('.','')
                            cols[3] = cols[3].replace('%','').replace(',','.')
    
                        if row in rows_tr[1:-5]:    
                            cols[0] = cols[0].split('. ')[1]   
                            cols[0:0] = [subdivision[i],'']
                        else:
                            cols.insert(0,subdivision[i])
                            cols.insert(2,'')

                        output_tbody.append([item for item in cols]) 
                    
                    select = Select(driver.find_element(By.ID,element_id))

            # sitio antiguo del SERVEL (solo incluye validamente emitidos)            
            else:
                FrameGuia = driver.find_element(By.NAME,'guiaFrame')    # panel lateral
                FrameMain = driver.find_element(By.NAME,'mainFrame')    # panel principal
                
                # Entrar a panel lateral
                driver.switch_to.frame(FrameGuia) 
                
                # click en 'Alfabetico'
                WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,'/html/body/form/table/tbody/tr[7]/td/div/a'))).click()
                
                # click en 'DATOS PAÍS'
                if rep == 0:
                    # DISTRITOS
                    WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,'/html/body/p[1]/a[4]'))).click()
                else:
                    # CIRCUNSCRIPCIONES
                    WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,'/html/body/p[1]/a[3]'))).click()
                
                # seleccionar subdivisión
                label = [{0:'Distrito ', 1:'Circ. Senatorial '}[rep] +str(i) for i in subdivision]
                
                output_tbody = []
                
                for i in range(0,len(label)):
                    WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.LINK_TEXT,label[i])) ).click()   
                        
                    # webscraping del panel principal
                    driver.switch_to.default_content()
                    driver.switch_to.frame(FrameMain) 
                    
                    # web scraping via BS4    
                    html = driver.page_source
                    soup = BeautifulSoup(html,'html.parser')
                            
                    table_html = soup.find_all('table')[2]  
                    rows_tr = table_html.find_all('tr')
                
                    for row in rows_tr[1:]:
                        cols = row.find_all('td')
                        cols = [item.text.strip() for item in cols]
                        if cols:
                            cols[2] = cols[2].replace('.','')
                            cols[3] = cols[3].replace('%','').replace(',','.')
                        # cols.insert(0,subdivision[i])
                        
                        if row in rows_tr[1:-1]:
                            cols[0:0] = [subdivision[i],'']     
                        else:
                            cols[3] = '100'
                            cols.insert(0,subdivision[i])
                            cols.insert(2,'')
                        output_tbody.append([item for item in cols]) 
                
                    # volver al panel lateral para escoger la siguiente subdivision
                    driver.switch_to.default_content()
                    driver.switch_to.frame(FrameGuia)         
                    
            candidatos = pd.DataFrame.from_records(output_tbody, columns = header)            
            candidatos['Lista/Pacto'] = candidatos['Lista/Pacto'].replace({'Válidamente Emitidos': 'Válidamente emitidos',
                                                                           'Votos Nulos': 'Nulos',
                                                                           'Votos en Blanco': 'Blancos',
                                                                           'Total Votación': 'Total'})            
        elif eleccion == 1973:
            header = [subdivrow,'Lista/Pacto','Candidatos', 'Partido', 'Votos', 'Porcentaje', 'Electos']
            
            table_html = soup.find_all('table', class_="wikitable")        
                    
            for i in (range(0,29) if (rep == 0) else range(29,34)):
                rows_tr = table_html[i].tbody.find_all('tr')
                aux = []
                subdivision = ((i+1) if i < 6 else (65+i if i<9 else i-1)) if (rep == 0) else (i-28)*2
                    
                for row in rows_tr[1:-1]:
                    cols = row.find_all('td')
                    cols = [item.text.strip() for item in cols]        
            
                    if row in rows_tr[1:-5]:
                        # candidatos, listas, pactos
                        if len(cols) == 1:
                            aux = cols[0].split('. ')[1]
                            continue
                        else: 
                            cols[2] = re.sub(r"\s+", "", cols[2], flags=re.UNICODE)
                            cols[3] = cols[3].replace('%','').replace(',','.')
                            cols.insert(0,aux)            
                    else:
                        # estadística
                        cols[1] = re.sub(r"\s+", "", cols[1], flags=re.UNICODE)
                        cols[2] = cols[2].replace('%','').replace(',','.')
                        cols[1:1] = ['','']
     
                    cols.insert(0,subdivision)
                    output_tbody.append(cols)                             
    
            candidatos = pd.DataFrame.from_records(output_tbody, columns = header)
            candidatos['Lista/Pacto'] = candidatos['Lista/Pacto'].replace({'Votos válidamente emitidos': 'Válidamente emitidos',
                                                                           'Votos nulos': 'Nulos',
                                                                           'Votos en blanco': 'Blancos',
                                                                           'Total de votos emitidos': 'Total'})
    
        else:
            # en este caso es una lista de electos
            header = [subdivrow,'Lista/Pacto','Candidatos', 'Partido', 'Votos', 'Porcentaje', 'Electos', 'Electos_comp', 'url']
                       
            list_html = soup.find_all('li', class_="clearfix")
                
            for i in range(0,len(list_html)):
                page_id = list_html[i].img['page_id']
                url = 'https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/'+page_id
                try:
                    localidad, partido = itemgetter(2,4)(list(list_html[i].small.stripped_strings))
                except IndexError:
                    localidad, partido = list(list_html[i].small.stripped_strings)[2], ''
                    
                output_tbody.append([re.sub(r'\ ".*?\"', '', localidad).replace(' Agrupación Departamental','').replace(' Distrito','').lower(), None, page_id.replace("_"," "), partido, "", "", "*", "*", url])
    
            candidatos = pd.DataFrame.from_records(output_tbody, columns = header)
            
            # agregar número de cada distrito/circunscripción (1925-1973)
            if eleccion >= 1925:
                agrupaciones_dep = {'prim': '1', 'seg': '2', 'ter': '3', 'cuar': '4', 
                                    'qui': '5', 'sex': '6', 'sép': '7', 'oct': '8', 'nov': '9', 
                                    'dec':'1', 'duodéc':'12', 'déc': '10', 'undéc':'11', 'vige':'2', 'vigé':'20'}
                
            elif eleccion >= 1912: 
                agrupaciones_dep = {'tarapacá': '1', 'taltal': '2', 'antofagasta': '3', 'copiapó': '4', 'la serena': '5',
                                    'ovalle': '6', 'petorca': '7', 'san felipe': '8', 'quillota': '9', 'valparaíso': '10',
                                    'santiago': '11', 'victoria': '12', 'rancagua': '13', 'caupolicán': '14', 'san fernando': '15',
                                    'santa cruz': '16', 'curicó': '17', 'talca': '18', 'lontué': '19', 'parral': '20',
                                    'linares': '21', 'constitución': '22', 'itata': '23', 'san carlos': '24', 'chillán': '25',
                                    'yungay': '26', 'coelemu': '27', 'concepción': '28', 'lautaro': '29', 'rere': '30',
                                    'arauco': '31', 'laja': '32', 'angol': '33', 'collipulli': '34', 'temuco': '35',
                                    'valdivia': '36', 'osorno': '37', 'llanquihue': '38', 'ancud': '39', 'castro': '40'} 

            numeros = re.compile("|".join(agrupaciones_dep))
            candidatos[subdivrow] = candidatos[subdivrow].map(lambda y: "".join(agrupaciones_dep[w] for w in numeros.findall(y)) if eleccion >= 1925 else agrupaciones_dep[numeros.search(y)[0]] )
    
            if len(candidatos[candidatos[subdivrow]=='']) > 0:
                candidatos.loc[candidatos[subdivrow]=='', subdivrow] = '0'
            
            candidatos[subdivrow] = candidatos[subdivrow].astype(int)

#%% CREAR Y FORMATEAR TABLAS

    # diccionario de partidos-listas
    pactos = pactos_electorales(eleccion)
    estadistica = ['Válidamente emitidos','Nulos','Blancos','Total'] if (eleccion == 1973 or eleccion >= 2013) else (['Válidamente emitidos'] if eleccion >= 1989 else ['Válidamente emitidos','Blancos/Nulos','Total'])
        
    if eleccion >= 1973:
        """ 
        SERVEL (1989-2021) y Wikipedia (1973) entregan los datos de la elección completa. 
        Se organizan en «candidatos», «partidos» y «listas».
        """
    
        # CANDIDATOS
        # corregir inconsistencias en siglas de partidos    
        if eleccion >= 1989:
            candidatos['Partido'] = candidatos['Partido'].str.replace(r'(P(S|C|L))CH',r'\1',regex=True)            

            if eleccion == 2021:
                candidatos['Partido'] = candidatos['Partido'].replace({'CONVERGENCIA':'CS'})
            if eleccion in {2013, 2017}:
                candidatos['Partido'] = candidatos['Partido'].replace({'FRVS':'FREVS', 'CIUD':'CIUDADANOS', 'AMPLI':'AMPLITUD'})        
            elif eleccion == 2009:
                candidatos['Partido'] = candidatos['Partido'].replace({'PE':'PEV'})
            elif eleccion in {1989, 1993, 1997}:
                candidatos['Partido'] = candidatos['Partido'].replace({'DC':'PDC', 'PDS':'SUR'})        
                        
            candidatos['Lista/Pacto'] = candidatos.apply(lambda row: row['Partido'] if (row['Lista/Pacto'] == '') else row['Lista/Pacto'],axis=1)                       
            candidatos['Lista/Pacto'] = candidatos['Lista/Pacto'].replace(pactos)
            
            # independientes en lista (hasta 2013)
            candidatos['Partido'] = candidatos['Partido'].str.replace(r'IL[A-Z]','IND',regex=True)     
        else:
            candidatos['Partido'] = candidatos['Partido'].str.replace(r'(P(S|C))Ch',r'\1',regex=True) 
            
            candidatos['Partido'][candidatos['Candidatos'] == 'Votos de Lista'] = 'VL-'+candidatos['Partido'][candidatos['Candidatos'] == 'Votos de Lista']
            candidatos['Candidatos'][candidatos['Candidatos'] == 'Votos de Lista'] = ''
        
        candidatos['Votos'] = candidatos['Votos'].astype(int)
        candidatos['Porcentaje'] = candidatos['Porcentaje'].astype(float)
        candidatos['Electos'][candidatos['Electos'] != ''] = '*'
        candidatos['Electos_comp'] = candidatos['Electos']
        if not 'url' in candidatos.columns: candidatos['url'] = ''
         
        candidatos[subdivrow] = candidatos[subdivrow].astype(int)
    
        candidatos = candidatos[[subdivrow, 'Lista/Pacto', 'Partido', 'Candidatos', 'Votos', 'Porcentaje', 'Electos', 'Electos_comp', 'url']]
        
        if not flag_reload:                       
            # eventuales inconsistencias en «válidamente emitidos»
            candidatos.loc[candidatos['Lista/Pacto'] == 'Válidamente emitidos','Votos'] = candidatos[candidatos['Partido']!= ''].groupby([subdivrow],sort=False).agg({'Votos':'sum'}).astype(int).values        
            candidatos.loc[candidatos['Lista/Pacto'] == 'Total','Votos'] = candidatos[candidatos['Lista/Pacto'].isin(estadistica[0:-1])].groupby([subdivrow],sort=False).agg({'Votos':'sum'}).astype(int).values        
            candidatos['Votos'] = candidatos['Votos'].astype(int)

            # VOTOS POR PARTIDOS POLITICOS
            pp = candidatos.copy()
            pp = pp.rename(columns={'Candidatos':'Candidaturas'})
     
            pp['Candidaturas'] = 1 
            pp.loc[pp['Lista/Pacto'].isin(estadistica),'Candidaturas'] = 0
    
            pp['Electos'] = pp['Electos'].map(lambda x: 1 if x == '*' else 0).astype(int)
                
            # las candidaturas independientes fuera de pacto no se agrupan
            pp = pd.concat([pp[(pp['Lista/Pacto'] != 'Candidatura Independiente') & (pp['Partido'] == 'IND') & (pp['Partido'] == '')].groupby([subdivrow, 'Lista/Pacto']).agg({'Partido':'first', 'Candidaturas':'sum', 'Votos':'sum', 'Porcentaje':'sum', 'Electos':'sum'}).reset_index(),
                            pp[(pp['Partido'] != 'IND') & (pp['Partido'] != '')].groupby([subdivrow, 'Partido']).agg({'Lista/Pacto':'first', 'Candidaturas':'sum', 'Votos':'sum', 'Porcentaje':'sum', 'Electos':'sum'}).reset_index(),
                            pp[pp['Lista/Pacto'] == 'Candidatura Independiente'],
                            pp[pp['Partido'] == ''],                    
                            ])
            
            # 1973
            pp.loc[pp['Partido'].str.contains('VL'),'Candidaturas'] = 0
            pp.loc[pp['Partido'].str.contains('VL'),'Candidaturas'] = 0
            
            pp = pp[[subdivrow,'Lista/Pacto','Partido','Candidaturas', 'Votos', 'Porcentaje', 'Electos']]
            
            # VOTOS POR LISTAS        
            listas = candidatos.copy()    
            listas = listas.rename(columns={'Candidatos':'Candidaturas'})
            
            listas['Candidaturas'] = 1
            listas.loc[listas['Lista/Pacto'].isin(estadistica),'Candidaturas'] = 0
    
            listas['Electos'] = listas['Electos'].map(lambda x: 1 if x == '*' else 0).astype(int)
            
            # las candidaturas independientes fuera de pacto no se agrupan
            listas = pd.concat([listas[listas['Lista/Pacto'] == 'Candidatura Independiente'],
                                listas[listas['Lista/Pacto'] != 'Candidatura Independiente'].groupby([subdivrow, 'Lista/Pacto']).sum().reset_index()
                                ]).drop(['Partido'],axis=1)
                           
            # 1973: correccion por votos de lista
            if eleccion == 1973:
                listas['Candidaturas'] = listas['Candidaturas'].map(lambda x: x-1 if x>=1 else x)

            listas = listas[[subdivrow,'Lista/Pacto','Candidaturas', 'Votos', 'Porcentaje', 'Electos']]
            
        # Senadores del período pasado van en «candidatos»
        # diputados/senadores reemplazantes van en «electos»            
        (candidatos, electos) = parlamentarios1973_presente(path_datos, candidatos, eleccion, rep)
            
    else:
        """
        La BCN posee los listados de cada legislatura. Se corrigen y diferencian entre quienes ganaron la elección
        correspondiente y complementarias, para formar el dataframe «candidatos» (llamado así por coherencia).
        Los datos de «partidos» y «listas» se construyen aparte, el primero mediante la función *resultados_pdba*, 
        de estar disponibles.
        """    
                        
        ## cambiar partidos a siglas, generar pactos
        siglas = siglas_partidos()    
        siglas_re = re.compile("|".join(siglas)) 

        ## corregir inconsistencias de la BCN, agregar senadores del período anterior
        if eleccion >= 1925:
            candidatos = parlamentarios1925_1969(path_datos, candidatos, eleccion, rep, siglas if flag_reload else None)

        if pactos:
            candidatos['Partido'] = candidatos['Partido'].map(lambda y: siglas[siglas_re.findall(y)[0]] if siglas_re.findall(y) else y)            
            candidatos['Lista/Pacto'] = candidatos['Partido'].map(lambda y: pactos[y] if y in pactos.keys() else '')        
        else:
            siglas_inv = {v: k for k, v in siglas.items()}    

            candidatos['Lista/Pacto'] = candidatos['Partido'].map(lambda y: siglas_inv[y] if y in siglas_inv.keys() else y) 
            candidatos['Partido'] = candidatos['Partido'].map(lambda y: siglas[siglas_re.findall(y)[0]] if siglas_re.findall(y) else y)
                
        pp = resultados1925_1969(candidatos, eleccion, rep, pactos, siglas)
        
        if pp is not None: 
            listas = pp.copy() 
            listas = listas.groupby([subdivrow, 'Lista/Pacto']).sum().reset_index()
        else: 
            listas = None                
                        
    # desde 2013 los nombres vienen en formato «apellido nombre»
    candidatos['Candidatos'] = nombres_formato(candidatos, formato = (True if flag_reload else (eleccion <= 2009)) )

    if eleccion >= 1973:
        print('Datos BCN candidatos')   
        biografiasBCN(eleccion, rep, candidatos)

    # indice categorico
    cat = list(dict.fromkeys(list(pactos.values()))) if pactos else candidatos['Lista/Pacto'].unique().tolist() 
    cat.extend(estadistica)            
    candidatos['Lista/Pacto'] = pd.Categorical(candidatos['Lista/Pacto'], categories=(cat[0:-3] if eleccion <= 1969 else cat), ordered=True) 
    candidatos.sort_values('Lista/Pacto',inplace=True)  
    candidatos = candidatos.sort_values([subdivrow,'Lista/Pacto'], ascending=[True,True])    
    candidatos = candidatos.set_index([subdivrow,'Lista/Pacto','Partido'])

    if pp is not None:  
        pp['Lista/Pacto'] = pd.Categorical(pp['Lista/Pacto'], categories=cat, ordered=True) 
        pp.sort_values('Lista/Pacto',inplace=True)    
        pp = pp.sort_values([subdivrow,'Lista/Pacto'], ascending=[True,True])
        pp = pp.set_index([subdivrow,'Lista/Pacto','Partido'])
    
        listas['Lista/Pacto'] = pd.Categorical(listas['Lista/Pacto'], categories=cat, ordered=True) 
        listas.sort_values('Lista/Pacto',inplace=True)    
        listas = listas.sort_values([subdivrow,'Lista/Pacto'], ascending=[True,True])
        listas = listas.set_index([subdivrow,'Lista/Pacto'])
        
        if eleccion >= 1973:        
            # corrección de porcentajes (agregarlos no es suficiente)
            total = estadistica[-1]
    
            pp['Porcentaje'] = round(100*pp['Votos']/pp.index.get_level_values(subdivrow).map(pp[pp.index.get_level_values('Lista/Pacto').isin([total])].droplevel([1,2])['Votos']),2)
            listas['Porcentaje'] = round(100*listas['Votos']/listas.index.get_level_values(subdivrow).map(listas[listas.index.get_level_values('Lista/Pacto').isin([total])].droplevel(1)['Votos']),2)

#%% GUARDAR DATOS
    if subdiv == None:
        prefix_filename = ''.join(['Eleccion',str(eleccion),'_',{0:'Distrito',1:'Circunscripcion'}[rep]])

    candidatos.to_csv(path_datos/(prefix_filename+ ('_candidatos.csv' if eleccion >= 1973 else '_electos.csv') ))          

    if eleccion >= 1973 and not flag_reload:        
        electos['Candidatos'] = nombres_formato(electos, formato = (True if flag_reload else (eleccion <= 2009)) )        
        electos = electos.sort_values([subdivrow,'Lista/Pacto'], ascending=[True,True])    
        electos = electos.set_index([subdivrow,'Lista/Pacto','Partido'])

        electos = pd.merge(electos, candidatos[candidatos['Electos'] == '*'][['Candidatos','url']],
                           how="outer",
                           on=[subdivrow, 'Lista/Pacto', 'Partido','Candidatos', 'url'])

        print('Datos BCN electos')   
        biografiasBCN(eleccion, rep, electos)
        
        electos.to_csv(path_datos/(prefix_filename+'_electos.csv'))

    if pp is not None: 
        listas.to_csv(path_datos/(prefix_filename+'_listas.csv'))
        pp.to_csv(path_datos/(prefix_filename+'_pp.csv'))
                       
    return(listas,pp,candidatos)                
