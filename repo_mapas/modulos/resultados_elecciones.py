#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrae/construye la información electoral usando diversas fuentes, mediante 
la función *resultados_parlamentarias*. La información varía según la elección, 
por lo que se observan dos períodos : 

- 1973-2021, con resultados detallados a nivel nacional, extraídos del SERVEL (1989-)
y wikipedia (1973). En el caso de la elección de senadores, la función 
*Senado1989_presente* armoniza la información entre una elección y la anterior, 
para visualizar la conformación de dicha cámara en el mapa final.

- 1941-1969, correspondiente a la conformación de la cámara de diputados. 
Diversas informaciones son corregidas usando *elecciones1925_1969*. En caso 
de tener resultados a nivel provincial, estos se agregan usando la función *resultados_pdba*.

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
from resultados_miscelaneo import nombres_formato


def resultados_parlamentarias(path_datos, eleccion, rep, subdiv=None):
    """
    Webscraping de las elecciones de diputados y/o senadores en 1941-2021, 
    desde los sitios web del SERVEL histórico (1989-2021), wikipedia (1973) y 
    BCN (1941-1969).
    
    Parámetros
    ----------
    path_datos : PosixPath
        Directorio.
    eleccion : int
        Año de la elección.
    rep : int
        Elección de diputados (0) o senadores (1).
    subdiv : list[int], opcional
        Lista de distritos o circunscripciones. Toma por defecto los del año correspondiente.        

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
        columnas = ['Candidatos', 'Votos', 'Porcentaje', 'Electos']  
        
    (Notar que 'Lista/Pacto' sigue un orden categórico.)
    
    """        

    if not eleccion in set(range(1941,1977,4)).union(set(range(1989,2025,4))):
        raise Exception()
        
    ## Distritos/agrupaciones departamentales o  circunscripciones/agrupaciones senatoriales por elección
    if rep == 0:        
        if eleccion >= 1989:
            subdivision = list(range(1,28+32*(eleccion <= 2013)+1))
        elif eleccion >= 1941:
            subdivision = list(range(1,28 if eleccion >= 1969 else 27))
    else:
        if eleccion == 2021:
            subdivision = [3,5,7,8,10,12,13,15,16]        
        elif eleccion == 2017:
            subdivision = [1,2,4,6,9,11,14]
        elif eleccion in {1997, 2005, 2013}:
            subdivision = [2,4,7,8,9,12,13,16,17,19]
        elif eleccion in {1993, 2001, 2009}:
            subdivision = [1,3,5,6,10,11,14,15,18]    
        elif eleccion == 1989:
            subdivision = list(range(1,20))
        else: 
            Exception()

    if subdiv != None:
          subdivision = list(set(subdiv).intersection(set(subdivision)))
            
          if not subdivision:
              Exception()
            
    subdivrow = {0:'Distrito',1:'Circunscripción'}[rep]

    
#%% CANDIDATOS
    if subdiv == None: 
        datos_filenames = sorted(path_datos.glob('*'+{0:'Distrito',1:'Circunscripcion'}[rep]))
    else:
        datos_filenames = sorted(path_datos.glob(''.join(['*',{0:'Distrito',1:'Circunscripcion'}[rep],'_',subdiv_str(subdivision)])))
        
    if datos_filenames:
        for file in datos_filenames: 
            filename = re.split('_|.csv',file.as_posix())[-2]
            
            if ('electos' in filename and eleccion <= 1969) or ('candidatos' in filename and eleccion == 1973):
                cols = [subdivrow,'Lista/Pacto','Candidatos', 'Partido', 'Votos', 'Porcentaje', 'Electos', 'Electos_comp', 'url'] if eleccion <= 1969 else [subdivrow,'Lista/Pacto', 'Partido', 'Candidatos', 'Votos', 'Porcentaje', 'Electos']

                candidatos = pd.read_csv(file)
                candidatos = candidatos[cols]
                candidatos = candidatos.fillna('')                  
                
                candidatos['Candidatos'] = candidatos['Candidatos'].apply(lambda x : literal_eval(str(x))).apply(' '.join)
                
    else:                        
        # WEBSCRAPING
        # iniciar selenium en Chrome   
        chrome_service = Service('/usr/bin/chromedriver')
        chrome_options = Options()
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument('--headless') 
        
        driver = webdriver.Chrome(options=chrome_options, service=chrome_service)

        if 2013 <= eleccion <= 2021:
            if eleccion == 2021:
                website = '234'*(rep == 0) +'233'*(rep == 1)
            elif eleccion == 2017:
                website = '215'*(rep == 0) +'220'*(rep == 1)
            else:
                website = '4'*(rep == 0) +'3'*(rep == 1)
            
            url = ''.join(['https://historico.servel.cl/servel/app/index.php?r=EleccionesGenerico&id=',website]) 
            
        elif 1989 <= eleccion <= 2009:
            url = ''.join(['https://historico.servel.cl/SitioHistorico/index',str(eleccion),{0:'_dipu.htm', 1:'_sena.htm'}[rep]])
        elif eleccion == 1973:
            url = 'https://es.wikipedia.org/wiki/Anexo:Resultados_de_las_elecciones_parlamentarias_de_Chile_de_1973'
        elif 1941 <= eleccion <= 1969:
            # ADAPTAR A SENADORES
            url = ''.join(['https://www.bcn.cl/historiapolitica/corporaciones/periodo_detalle?inicio=',str(eleccion),'-05-21&fin=',str(eleccion+4),'-05-20&periodo=1925-1973&cam=Diputados'])    
        
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
            # ADAPTAR A SENADORES
            header = [subdivrow,'Lista/Pacto','Candidatos', 'Partido', 'Votos', 'Porcentaje', 'Electos']
            
            table_html = soup.find_all('table', class_="wikitable")        
                    
            for i in range(0,29):
                rows_tr = table_html[i].tbody.find_all('tr')
                aux = []
                subdiv = (i+1) if i < 6 else (65+i if i<9 else i-1)
                    
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
     
                    cols.insert(0,subdiv)
                    output_tbody.append(cols)                             
    
            candidatos = pd.DataFrame.from_records(output_tbody, columns = header)
            candidatos['Lista/Pacto'] = candidatos['Lista/Pacto'].replace({'Votos válidamente emitidos': 'Válidamente emitidos',
                                                                           'Votos nulos': 'Nulos',
                                                                           'Votos en blanco': 'Blancos',
                                                                           'Total de votos emitidos': 'Total'})
    
        else:
            # ADAPTAR A SENADORES
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
                    
                output_tbody.append([re.sub(r'\ ".*?\"', '', localidad).replace(' Agrupación Departamental','').replace(' Distrito','').lower(),"", page_id.replace("_"," "), partido, "", "", "*", "*", url])
    
            candidatos = pd.DataFrame.from_records(output_tbody, columns = header)
            
            # agregar número de cada distrito/circunscripción
            digitos = {'prim': '1', 'seg': '2', 'ter': '3', 'cuar': '4', 
                      'qui': '5', 'sex': '6', 'sép': '7', 'oct': '8', 'nov': '9', 
                      'dec':'1', 'duodéc':'12', 'déc': '10', 'undéc':'11', 'vige':'2', 'vigé':'20'}
            numeros = re.compile("|".join(digitos))
            
            candidatos[subdivrow] = candidatos[subdivrow].map(lambda y: "".join(digitos[w] for w in numeros.findall(y)) ).astype(int)


#%% CREAR Y FORMATEAR TABLAS

    # diccionario de partidos-listas
    pactos = pactos_electorales(eleccion)
    estadistica = ['Válidamente emitidos','Nulos','Blancos','Total'] if (eleccion == 1973 or eleccion >= 2013) else (['Válidamente emitidos'] if eleccion >= 1989 else ['Válidamente emitidos','Blancos/Nulos','Total'])
    
    # indice categorico (corregir para 1989 en adelante)
    cat = list(dict.fromkeys(list(pactos.values())))
    cat.extend(estadistica)
    
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
        candidatos[subdivrow] = candidatos[subdivrow].astype(int)
    
        candidatos = candidatos[[subdivrow, 'Lista/Pacto', 'Partido', 'Candidatos', 'Votos', 'Porcentaje', 'Electos']]
                                   
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
                       
        # 1973: correccion candidaturas
        if eleccion == 1973:
            listas['Candidaturas'] = listas['Candidaturas']-1 
    
    else:
        """
        La BCN posee los listados de cada legislatura. Se corrigen y diferencian entre quienes ganaron la elección
        correspondiente y complementarias, para formar el dataframe «candidatos» (llamado así por coherencia).
        Los datos de «partidos» y «listas» se construyen aparte, el primero mediante la función *resultados_pdba*, 
        de estar disponibles.
        """    
    
        # corregir inconsistencias de la BCN   
        candidatos = elecciones1925_1969(candidatos, eleccion, rep)
                    
        ## cambiar partidos a siglas, generar pactos
        siglas = siglas_partidos()    
        siglas_re = re.compile("|".join(siglas)) 
        
        candidatos['Partido'] = candidatos['Partido'].map(lambda y: siglas[siglas_re.findall(y)[0]] if siglas_re.findall(y) else y)                                                    
        candidatos['Lista/Pacto'] = candidatos['Partido'].map(lambda y: pactos[y] if y in pactos.keys() else '')        
                
        pp = resultados_pdba(candidatos, eleccion, rep, pactos, siglas)
        
        if pp:
            listas = pp.copy() 
            listas = listas.groupby([subdivrow, 'Lista/Pacto']).sum().reset_index()
        else: 
            listas = None
                
    # desde 2013 los nombres vienen en formato «apellido nombre»
    candidatos['Candidatos'] = nombres_formato(candidatos,formato=(eleccion <= 2009))
         
    candidatos['Lista/Pacto'] = pd.Categorical(candidatos['Lista/Pacto'], categories=(cat[0:-3] if eleccion <= 1969 else cat), ordered=True) 
    candidatos.sort_values('Lista/Pacto',inplace=True)    
    candidatos = candidatos.sort_values([subdivrow,'Lista/Pacto'], ascending=[True,True])
    candidatos = candidatos.set_index([subdivrow,'Lista/Pacto','Partido'])

    if pp: 
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
    else:            
        prefix_filename = ''.join(['Eleccion',str(eleccion),'_',{0:'Distrito',1:'Circunscripcion'}[rep],'_'+subdiv_str(subdivision)])
        
    candidatos.to_csv(path_datos/(prefix_filename+('_candidatos.csv' if eleccion >= 1973 else '_electos.csv')))

    if pp:
        listas.to_csv(path_datos/(prefix_filename+'_listas.csv'))
        pp.to_csv(path_datos/(prefix_filename+'_pp.csv'))
                       
    return(listas,pp,candidatos)

#%%
def subdiv_str(subdivision):
    """
    Toma una lista de enteros y la expresa como texto, abreviando grupos consecutivos. Por ejemplo
        subdiv_str([1,...,28]) = '1-28'
        subdiv_str([8,9,10,13,14,15,16]) = '8-10_13-16'

    Parámetros
    ---------
    subdivision : list[int]
        Lista de enteros.

    Entrega
    -------
    filename : str
        Texto para usar en los nombres de archivo.

    """
       
    subdivision = list(set(subdivision))
    subdivision.sort()    
    
    l0 = subdivision[0]
    l1 = subdivision[0]
    
    filename=''
    
    for i in range(1,len(subdivision)):
        if subdivision[i] == subdivision[i-1]+1:
            l1 = subdivision[i]
        else:
            filename = filename + (str(l0)+ ('-'+str(l1))*bool(l0 != l1))+'_'            

            l0 = subdivision[i]
            l1 = subdivision[i]
    
        if i == len(subdivision)-1:
            filename = filename + (str(l0)+'-'+str(l1))*bool(l0 != l1) +str(l0)*bool(l0==l1)
    
    return filename +bool(len(subdivision) == 1)*str(l0)


#%%
#%% 
def elecciones1925_1969(candidatos, eleccion, rep):
    """
    Corrección de datos electorales en el período 1941-1969, a partir de información
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

    if eleccion == 1969:
        #elecciones complementarias
        reemplazados = ['Pontigo Urrutia', 'Lacoste Navarro', 'Avendaño Ortúzar']
        reemplazantes = ['Altamirano Guerrero', 'Marín Socías', 'Diez Urzúa']
                
        #BCN 
        candidatos.loc[candidatos['Candidatos'].str.contains('Sabat Gozalo'), 'Partido'] = 'Partido Socialista'

        if not sum(candidatos['Candidatos'].str.contains('Juan Bautista Segundo Argandoña Cortéz')):        
            candidatos.loc[len(candidatos.index),:] = 2,'','Juan Bautista Segundo Argandoña Cortéz','Partido Demócrata Cristiano','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Bautista_Segundo_Argandoña_Cortéz'
            candidatos.loc[len(candidatos.index),:] = 71,'','Alvaro Erich Schnake Silva','Partido Socialista','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Alvaro_Erich_Schnake_Silva'

    elif eleccion == 1965:
        #elecciones complementarias
        reemplazados = ['Muñoz Horz', 'Coñuepán Huenchual']
        reemplazantes = ['Montedónico Nápoli', 'Merino Jarpa']        

        #BCN 
        candidatos.loc[candidatos['Candidatos'].str.contains('Lavandero Illanes'), 'Partido'] = 'Partido Demócrata Cristiano'
        candidatos.loc[candidatos['Candidatos'].str.contains("Melo Paéz"), 'Partido'] = 'Partido Comunista'
        candidatos.loc[candidatos['Candidatos'].str.contains("González Maertens"), 'Partido'] = 'Partido Democrático Nacional'
        
        if not sum(candidatos['Candidatos'].str.contains('Juan Bautista Segundo Argandoña Cortéz')):
            candidatos.loc[len(candidatos.index),:] = 2,'','Juan Bautista Segundo Argandoña Cortéz','Partido Demócrata Cristiano','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Bautista_Segundo_Argandoña_Cortéz'                
        
    elif eleccion == 1961: 
        #elecciones complementarias
        reemplazados = ['Pinto Díaz', 'Naranjo Jara']
        reemplazantes = ['Monckeberg Barros', 'Naranjo Arias']
        
        #BCN
        candidatos.loc[candidatos['Candidatos'].str.contains('Klein Doerner'), 'Partido'] = 'Partido Liberal'
        
        if not sum(candidatos['Candidatos'].str.contains('Ramón Augusto Silva Ulloa')):        
            candidatos.loc[len(candidatos.index),:] = 2,'','Juan Bautista Segundo Argandoña Cortéz','Partido Demócrata Cristiano','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Bautista_Segundo_Argandoña_Cortéz'
            candidatos.loc[len(candidatos.index),:] = 2,'','Ramón Augusto Silva Ulloa','Partido Socialista','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Ramón_Augusto_Silva_Ulloa'
            candidatos.loc[len(candidatos.index),:] = 6,'','Guillermo Rivera Bustos','Partido Liberal','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Guillermo_Rivera_Bustos' 
            candidatos.loc[len(candidatos.index),:] = 6,'','Alonso Zumaeta Faune','Partido Socialista','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Alonso_Zumaeta_Faune'
            candidatos.loc[len(candidatos.index),:] = 21,'','Juan Tuma Masso','Partido Democrático Nacional','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Tuma_Masso'        

    elif eleccion == 1957:
        # elecciones complementarias
        reemplazados = ['Zepeda Barrios', 'Rojas Wolff', 'Mallet Simonetti']
        reemplazantes = ['Mercado Illanes', 'Edwards Orrego', 'Zumaeta Faune']
        
        #BCN        
        candidatos.loc[candidatos['Partido'] == 'Partido Comunista de Chile', 'Partido'] = 'Partido del Trabajo'
        candidatos.loc[candidatos['Partido'] == 'Partido Demócrata Cristiano', 'Partido'] = 'Falange Nacional'
        candidatos.loc[candidatos['Partido'] == 'Partido Democrático del Pueblo', 'Partido'] = 'Partido Democrático'

        # fuente : la nacion, 5/3/1957, p.2; y 10/3/1957, p.4
        candidatos.loc[candidatos['Candidatos'].str.contains("Hurtado O'Ryan"), 'Partido'] = 'Partido Nacional'
        candidatos.loc[candidatos['Candidatos'].str.contains('Ahumada Trigo'), 'Partido'] = 'Partido Socialista'# 'del Trabajo'        
        candidatos.loc[candidatos['Candidatos'].str.contains('Oyarzún Decouvieres'), 'Partido'] = 'Partido Democrático'
        candidatos.loc[candidatos['Candidatos'].str.contains('Gormaz Molina'), 'Partido'] = 'Partido Nacional'
        candidatos.loc[candidatos['Candidatos'].str.contains('Lobos Arias'), 'Partido'] = 'Partido Nacional'
        candidatos.loc[candidatos['Candidatos'].str.contains('Serrano de Viale Rigo'), 'Partido'] = 'Partido Conservador Unido'
        candidatos.loc[candidatos['Candidatos'].str.contains('Widmer Ewertz'), 'Partido'] = 'Partido Nacional'
        candidatos.loc[candidatos['Candidatos'].str.contains('Valdés Solar'), 'Partido'] = 'Partido Nacional'
        candidatos.loc[candidatos['Candidatos'].str.contains('Lavandero Illanes'), 'Partido'] = 'Partido Nacional'
        candidatos.loc[candidatos['Candidatos'].str.contains('Raúl Aldunate Phillips'), 'Partido'] = 'Partido Nacional'
        candidatos.loc[candidatos['Candidatos'].str.contains('Momberg Roa'), 'Partido'] = 'Partido Nacional'       
        candidatos.loc[candidatos['Candidatos'].str.contains('Cademártori Invernizzi'), 'Partido'] = 'Partido Socialista'# 'del Trabajo'
        candidatos.loc[candidatos['Candidatos'].str.contains('Martones Morales'), 'Partido'] = 'Partido Democrático'
        candidatos.loc[candidatos['Candidatos'].str.contains('Meneses Dávila'), 'Partido'] = 'Independiente'#'Partido Liberal'

        if not sum(candidatos['Candidatos'].str.contains('Ramón Augusto Silva Ulloa')):
            candidatos.loc[len(candidatos.index),:] = 2,'','Ramón Augusto Silva Ulloa','Partido Socialista Popular','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Ramón_Augusto_Silva_Ulloa'
            candidatos.loc[len(candidatos.index),:] = 6,'','Alonso Zumaeta Faune','Partido Socialista','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Alonso_Zumaeta_Faune'
            candidatos.loc[len(candidatos.index),:] = 71,'','Luis Pareto González','Partido Agrario Laborista','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Luis_Pareto_González'
        
    elif eleccion == 1953:
        #elecciones complementarias
        reemplazados = ['Zárate Andreu', 'Montero Soto', 'Pizarro Cabezas', 'Benaprés Lafourcade', 'Nazar Feres', 'Recabarren Valenzuela','Muñoz San Martín']
        reemplazantes = ['Maurás Novella', 'Flores Álvarez', 'Corral Garrido', 'Pumarino Fuentes', 'Muñoz Horz', 'Gumucio Vives', 'Barja Blanco']
                
        #BCN
        
        #fuente : la nacion, 3/3/1953, pp.6 y 8
        candidatos.loc[candidatos['Candidatos'].str.contains('Palma Sanguinetti'), 'Partido'] = 'Partido Conservador Social Cristiano'
        candidatos.loc[candidatos['Candidatos'].str.contains('Jerez Contreras'), 'Partido'] = 'Movimiento Nacional Ibañista'
        candidatos.loc[candidatos['Candidatos'].str.contains('Naranjo Jara'), 'Partido'] = 'Partido Socialista Popular'
        candidatos.loc[candidatos['Candidatos'].str.contains('Muñoz San Martín'), 'Partido'] = 'Partido Agrario Laborista'
        candidatos.loc[candidatos['Candidatos'].str.contains('Lobos Arias'), 'Partido'] = 'Partido Agrario'
#        candidatos.loc[candidatos['Candidatos'].str.contains('Araneda Rocha'), 'Partido'] = 'Partido Liberal Progresista'
        candidatos.loc[candidatos['Candidatos'].str.contains('Echavarri Elorza'), 'Partido'] = 'Partido Agrario'
        candidatos.loc[candidatos['Candidatos'].str.contains('Palma Gallardo'), 'Partido'] = 'Partido Conservador Social Cristiano'
        candidatos.loc[candidatos['Candidatos'].str.contains('Hernández Barrientos'), 'Partido'] = 'Partido Socialista Popular'        
        candidatos.loc[candidatos['Candidatos'].str.contains('Acevedo Pavez'), 'Partido'] = 'Movimiento Nacional Ibañista' #'Partido Socialista Popular'
        candidatos.loc[candidatos['Candidatos'].str.contains('Ojeda Doren'), 'Partido'] = 'Unión Nacional de Independientes'
        candidatos.loc[candidatos['Candidatos'].str.contains('Rivera González'), 'Partido'] = 'Partido Laborista'
        candidatos.loc[candidatos['Candidatos'].str.contains('Justiniano Préndez'), 'Partido'] = 'Unión Nacional de Independientes'
        
        if not sum(candidatos['Candidatos'].str.contains('Ramón Augusto Silva Ulloa')):
            candidatos.loc[len(candidatos.index),:] = 2,'','Ramón Augusto Silva Ulloa','Partido Socialista Popular','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Ramón_Augusto_Silva_Ulloa'        
            candidatos.loc[len(candidatos.index),:] = 17,'','Adán Puentes Gómez','Partido Democrático del Pueblo','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Adán_Puentes_Gómez'        
            candidatos.loc[len(candidatos.index),:] = 19,'','Jorge Rigo Righi Caridi','Partido Agrario Laborista','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Jorge_Rigo_Righi_Caridi'        
            candidatos.loc[len(candidatos.index),:] = 21,'','Edgardo Barrueto Reeve','Partido Agrario Laborista','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Edgardo_Barrueto_Reeve'               
            candidatos.loc[len(candidatos.index),:] = 71,'','Eduardo Maass Jensen','Partido Socialista Popular','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Edgardo_Maass_Jensen'        

    elif eleccion == 1949: 
        reemplazados = ['Souper Maturana', 'Bravo Santibáñez', 'Muñoz García', 'Maira Castellón', 'Cifuentes Sobarzo', 'Cárdenas Núñez', 'Concha Molina']
        reemplazantes = ['Cruz Ponce', 'Noguera Prieto', 'Inés Leonor Enríquez Frodden', 'Puga Fisher', 'Puga Vega']

        #BCN
        candidatos.loc[candidatos['Partido'] == 'Partido Conservador', 'Partido'] = 'Partido Conservador Social Cristiano'
        candidatos.loc[candidatos['Partido'] == 'Partido Social Cristiano', 'Partido'] = 'Partido Conservador Social Cristiano'
        
        #fuente: la nación, 8/3/1949, pp.1-2
        candidatos.loc[candidatos['Candidatos'].str.contains('Torres Galdames'), 'Partido'] = 'Partido Radical Democrático'
        candidatos.loc[candidatos['Candidatos'].str.contains('Galleguillos Clett'), 'Partido'] = 'Partido Socialista Popular'        
        candidatos.loc[candidatos['Candidatos'].str.contains('Pizarro Cabezas'), 'Partido'] = 'Partido Liberal'        
#        candidatos.loc[candidatos['Candidatos'].str.contains('Arqueros Rodríguez'), 'Partido'] = 'Partido Conservador Social Cristiano' 
        candidatos.loc[candidatos['Candidatos'].str.contains('Rivas Fernández'), 'Partido'] = 'Partido Radical Democrático'
        candidatos.loc[candidatos['Candidatos'].str.contains('Arenas Aguiar'), 'Partido'] = 'Partido Radical Democrático'
        candidatos.loc[candidatos['Candidatos'].str.contains('Martones Quezada'), 'Partido'] = 'Partido Democrático del Pueblo'
        candidatos.loc[candidatos['Candidatos'].str.contains('Tapia Moore'), 'Partido'] = 'Partido Socialista Popular'
        candidatos.loc[candidatos['Candidatos'].str.contains('Rodríguez Arenas'), 'Partido'] = 'Partido Socialista Popular'
        candidatos.loc[candidatos['Candidatos'].str.contains('Braun Page'), 'Partido'] = 'Partido Liberal'
        candidatos.loc[candidatos['Candidatos'].str.contains('Olavarría Alarcón'), 'Partido'] = 'Partido Socialista Popular'
        candidatos.loc[candidatos['Candidatos'].str.contains('Castro Palma'), 'Partido'] = 'Partido Socialista Popular'
#        candidatos.loc[candidatos['Candidatos'].str.contains('Muñoz García'), 'Partido'] = 'Partido Liberal'
        candidatos.loc[candidatos['Candidatos'].str.contains('Mejías Concha'), 'Partido'] = 'Partido Radical Democrático'
        candidatos.loc[candidatos['Candidatos'].str.contains('Moller Bordeu'), 'Partido'] = 'Partido Radical Democrático'
        candidatos.loc[candidatos['Candidatos'].str.contains('Sepúlveda Rondanelli'), 'Partido'] = 'Partido Radical Democrático'
        candidatos.loc[candidatos['Candidatos'].str.contains('Echavarri Elorza'), 'Partido'] = 'Partido Agrario Laborista'
        candidatos.loc[candidatos['Candidatos'].str.contains('Durán Neumann'), 'Partido'] = 'Partido Radical Democrático'
        candidatos.loc[candidatos['Candidatos'].str.contains('Alfonso Campos Menéndez'), 'Partido'] = 'Partido Liberal'
        candidatos.loc[candidatos['Candidatos'].str.contains('Barrientos Villalobos'), 'Partido'] = 'Partido Radical'
        candidatos.loc[candidatos['Candidatos'].str.contains('Raúl Aldunate Phillips'), 'Partido'] = 'Partido Liberal'

        if not sum(candidatos['Candidatos'].str.contains('Edgardo Barrueto Reeve')):                        
            candidatos.loc[len(candidatos.index),:] = 21,'','Edgardo Barrueto Reeve','Partido Liberal Progresista','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Edgardo_Barrueto_Reeve'               
            candidatos.loc[len(candidatos.index),:] = 24,'','José Edesio García Setz','Partido Conservador Social Cristiano','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Edesio_García_Setz'        
        
    elif eleccion == 1945:
        reemplazados = ['Cisternas Ortíz', 'Escala Garnham', 'Carrasco Rábago', 'Cabezón Díaz', 'Madrid Osorio', 'Cifuentes Latham', 'Chesta Pastoureaud', 'del Canto Medán',
                        'Araya Zuleta', 'Echeverría Moorhouse', 'Edwards Atherton', 'Osorio Navarrete']
        reemplazantes = ['Avilés Avilés', 'Durán Villarreal', 'Wiegand Frodden', 'Bedoya Hundesdoerffer', 'Moore Montero', 'Zañartu Urrutia', 'Sandoval Muñoz', 'Rogers Sotomayor']
        
        #BCN
        candidatos.loc[candidatos['Partido'] == 'Partido Comunista de Chile', 'Partido'] = 'Partido Progresista Nacional'
        candidatos.loc[candidatos['Partido'] == 'Partido Agrario Laborista', 'Partido'] = 'Partido Agrario'
        
        #fuente : la nación, 5/3/1945, p.4
        candidatos.loc[candidatos['Candidatos'].str.contains('Rossetti Colombino'), 'Partido'] = 'Partido Socialista'
        candidatos.loc[candidatos['Candidatos'].str.contains('Echavarri Elorza'), 'Partido'] = 'Partido Agrario'
        candidatos.loc[candidatos['Candidatos'].str.contains('Escala Garnham'), 'Partido'] = 'Partido Conservador'        
        candidatos.loc[candidatos['Candidatos'].str.contains('Godoy Urrutia'), 'Partido'] = 'Partido Progresista Nacional'        
        candidatos.loc[candidatos['Candidatos'].str.contains('Coñuepán Huenchual'), 'Partido'] = 'Alianza Popular Libertadora'        
        candidatos.loc[candidatos['Candidatos'].str.contains('Bustos León'), 'Partido'] = 'Partido Liberal Progresista'

        if not sum(candidatos['Candidatos'].str.contains('Héctor Zañartu Urrutia')):
            candidatos.loc[len(candidatos.index),:] = 16,'','Héctor Zañartu Urrutia','Partido Conservador','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Héctor_Zañartu_Urrutia'
            candidatos.loc[len(candidatos.index),:] = 21,'','Braulio Sandoval Muñoz','Partido Agrario','','',None,'*',''            
            candidatos.loc[len(candidatos.index),:] = 25,'','Juan Rafael Del Canto Medán','Partido Liberal Democrático','','','*',None,'https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Rafael_Del_Canto_Medán'
            candidatos.loc[len(candidatos.index),:] = 71,'','Roberto Barros Torres','Partido Liberal','','','*',None,'https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Roberto_Barros_Torres'
                
    elif eleccion == 1941: 
        reemplazados = ['Ollino Buzeta', 'Muñoz Ayling', 'Rosende Verdugo', 'Rossetti Colombino', 'Montecinos Matus', 'Labarca Moreno', 'Ernst Martínez', 'Castelblanco Agüero']
        reemplazantes = ['Ollino Buzeta', 'Baeza Herrera', 'Jara del Villar', 'Godoy Urrutia', 'Brito Salvo', 'Pinedo Goycochea', 'Campos Menéndez']

        #BCN
        candidatos.loc[candidatos['Partido'] == 'Partido Comunista de Chile', 'Partido'] = 'Partido Progresista Nacional'        
        
        # fuente : la nación, 4/3/1941, p.4
        candidatos.loc[candidatos['Candidatos'].str.contains('Labarca Moreno'), 'Partido'] = 'Partido Liberal'
        candidatos.loc[candidatos['Candidatos'].str.contains('Echavarri Elorza'), 'Partido'] = 'Partido Agrario'
        candidatos.loc[candidatos['Candidatos'].str.contains('González Von Marées'), 'Partido'] = 'Vanguardia Popular Socialista'
        candidatos.loc[candidatos['Candidatos'].str.contains('Ceardi Ferrer'), 'Partido'] = 'Falange Nacional'
        candidatos.loc[candidatos['Candidatos'].str.contains('Garretón Walker'), 'Partido'] = 'Falange Nacional'
        candidatos.loc[candidatos['Candidatos'].str.contains('Berman Berman'), 'Partido'] = 'Partido Socialista de Trabajadores'
        candidatos.loc[candidatos['Candidatos'].str.contains('Zamora Rivera'), 'Partido'] = 'Partido Progresista Nacional'        
        candidatos.loc[candidatos['Candidatos'].str.contains('Urrutia Infante'), 'Partido'] = 'Partido Liberal'
        candidatos.loc[candidatos['Candidatos'].str.contains('Fuentealba Troncoso'), 'Partido'] = 'Partido Demócrata'        
        candidatos.loc[candidatos['Candidatos'].str.contains('Bustos León'), 'Partido'] = 'Alianza Popular Libertadora'
        candidatos.loc[candidatos['Candidatos'].str.contains('Rossetti Colombino'), 'Partido'] = 'Partido Radical Socialista'

        if not sum(candidatos['Candidatos'].str.contains('César Godoy Urrutia')):
            candidatos.loc[len(candidatos.index),:] = 24,'','Alfonso Campos Menéndez','Partido Liberal','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Alfonso_Campos_Menéndez'            
            candidatos.loc[len(candidatos.index),:] = 25,'','Juan Rafael del Canto Medán','Partido Liberal Democrático','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Rafael_Del_Canto_Medán'
            candidatos.loc[len(candidatos.index),:] = 71,'','César Godoy Urrutia','Partido Progresista Nacional','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/César_Godoy_Urrutia'
        
    candidatos.loc[candidatos['Candidatos'].str.contains('|'.join(reemplazados)), 'Electos_comp'] = None
    candidatos.loc[candidatos['Candidatos'].str.contains('|'.join(reemplazantes)), 'Electos'] = None

    candidatos[subdivrow] = candidatos[subdivrow].astype(int)  

    #no considera como duplicados los agregados para corregir 
    electos = candidatos.drop_duplicates(subset=['Candidatos'], keep="last")

    #verificar si están todos los diputados
    if False:
        count = candidatos[candidatos['Electos'] == '*'].groupby(['Distrito']).agg({'Electos':'count'})    
        if eleccion <= 1965:
            count['escanos'] = [4,7,2,7,3,12,5,6,4,3,5,3,4,3,5,9,2,4,6,10,5,3,3,3,1,18,5,5]        
        elif eleccion <= 1973:
            count['escanos'] = [4,7,2,7,3,12,5,6,4,3,5,3,4,3,5,9,2,4,6,10,5,3,3,3,2,2,18,5,5]
        
        count['diff'] = count['escanos'] -count['Electos']
    
        print(count[count['diff'] != 0])
        print(candidatos[candidatos['Distrito'].isin(count[count['diff'] != 0].index)][['Distrito','Candidatos']].sort_values(['Candidatos']).sort_values(['Distrito']))
    
        print('')
        print(candidatos[(candidatos['Electos_comp'] == '*') & (candidatos['Electos'] != '*')]['Candidatos'])

    return candidatos

#%%    
def resultados_pdba(candidatos, eleccion, rep, pactos, siglas):        
    """
    A partir de las listas de candidatos y pactos, se construye un dataframe
    con los resultados de partidos, para los años 1945, 1961, 1965, 1969 y 1973.
    
    Fuentes : 
    - https://pdba.georgetown.edu/Elecdata/Chile/cong_totals.html
    - Urzua Valenzuela
    - Aldunate
    
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
    
    ##  resultados solo para diputados: los datos de estos años no cuadran    
    if ((rep == 0) and eleccion in {1941, 1949, 1953, 1957}) or (rep == 1):
        return None

    ## construir datos para {1945, 1961, 1965, 1969, 1973}
    subdivrow = {0:'Distrito',1:'Circunscripción'}[rep]
    
    pl = list(pactos.items())
    pl.extend([('','Válidamente emitidos'),('','Blancos/Nulos'),('','Total')])

    flatten_list = lambda test:[element for item in test for element in flatten_list(item)] if type(test) is list else [test]

    provincias = flatten_list(['Tarapacá', 'Antofagasta', 'Atacama', 'Coquimbo', 'Aconcagua', 'Valparaíso', 
                               ['Santiago-1', 'Santiago-2', 'Santiago-3', 'Santiago-4'], "O'Higgins", 'Colchagua', 'Curicó', 'Talca', 'Maule', 'Linares',
                               ['Nuble-1', 'Nuble-2'], 'Concepción', 'Arauco', 'Bío-Bío', 'Malleco', 'Cautín', 
                               'Valdivia', 'Osorno', 'Llanquihue', 'Chiloé', 'Aysén', 'Magallanes'])

    reg = list(range(1,28 if eleccion >= 1969 else 27))
    reg[7:7] = [71,72,73]
    reg.remove(7)

    agg = [0,0]

    if eleccion == 1969:        
        # Aldunate, p. 227
        pp = pd.merge(pd.DataFrame.from_records([(d,l,p) for d in provincias for p,l in pl], columns = ['Provincias', 'Lista/Pacto', 'Partido'] ),
                      pd.DataFrame({'Total': flatten_list([51915, 78262, 38564, 80236, 48296, 270671, [917937]*4, 85236, 43323, 29395, 52635, 23195, 44915,
                                                          [72873]*2, 167678, 21141, 39498, 41141, 89498, 62265, 40695, 39070, 25801, 11322, 30686]),
                                   'Provincias': provincias}),
                      how="outer")
              
        
        pp.loc[pp['Partido'] == siglas['Partido Comunista'],'Votos'] = flatten_list([16563, 18121, 7991, 13331, 6221, 60366, [152818]*4, 10458, 2289, 3496, 8765, 0, 2525,
                                                                                   [5298]*2, 43725, 4948, 7748, 2556, 6894, 2729, 0, 0, 0, 2381, 3182])
        pp.loc[pp['Partido'] == siglas['Partido Demócrata Cristiano'],'Votos'] = flatten_list([13953, 20814, 10103, 19919, 13730, 87249, [279720]*4, 22891, 11840, 9175, 15617, 5702, 14591,
                                                                                             [20493]*2, 49834, 5198, 10629, 12706, 31693, 16929, 9873, 11264, 6690, 3675, 10284])
        pp.loc[pp['Partido'] == siglas['Partido Democrático Nacional'],'Votos'] = flatten_list([458, 1725, 223, 773, 590, 3726, [12479]*4, 980, 763, 455, 5996, 2842, 192,
                                                                                              [440]*2, 3731, 182, 1053, 460, 4990, 1219, 477, 455, 79, 104, 396])
        pp.loc[pp['Partido'] == siglas['Partido Nacional'],'Votos'] = flatten_list([9231, 6350, 2646, 10635, 11264, 49601, [209895]*4, 18930, 10020, 4745, 10627, 5683, 8348,
                                                                                  [14402]*2, 18478, 0, 8761, 9957, 28986, 13499, 6961, 10162, 8048, 2229, 1157])
        pp.loc[pp['Partido'] == siglas['Partido Radical'],'Votos'] = flatten_list([5677, 17189, 8482, 15962, 6332, 32816, [76623]*4, 7831, 8708, 5581, 9656, 4981, 9045,
                                                                                 [19964]*2, 23293, 5048, 6218, 10985, 9235, 6816, 11382, 4488, 6135, 904, 3289])
        pp.loc[pp['Partido'] == siglas['Partido Social Demócrata'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 940, [6003]*4, 3097, 0, 0, 856, 3506, 0,
                                                                                          [0]*2, 1462, 0, 0, 0, 4751, 0, 0, 0, 0, 0, 0])
        pp.loc[pp['Partido'] == siglas['Partido Socialista'],'Votos'] = flatten_list([2035, 4138, 7625, 14628, 4263, 21933, [126828]*4, 12966, 7500, 4071, 0, 0, 3176,
                                                                                    [9468]*2, 19450, 2379, 3926, 1388, 0, 17319, 9748, 7616, 3726, 0, 10426])
        pp.loc[pp['Partido'] == siglas['Unión Socialista Popular'],'Votos'] = flatten_list([2071, 6885, 270, 2138, 3399, 1135, [8382]*4, 3980, 643, 1151, 0, 0, 5943,
                                                                                          [0]*2, 1854, 2529, 0, 2002, 1167, 1192, 587, 1984, 317, 1565, 924])
        pp.loc[pp['Partido'] == siglas['Independiente'],'Votos'] = flatten_list([15, 0, 0, 0, 0, 0, [2105]*4, 0, 0, 0, 0, 0, 0,
                                                                               [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    elif eleccion == 1965:        
        # Aldunate, p. 217, 221
        pp = pd.merge(pd.DataFrame.from_records([(d,l,p) for d in provincias for p,l in pl], columns = ['Provincias', 'Lista/Pacto', 'Partido'] ),
                      pd.DataFrame({'Total_v': flatten_list([26173, 42610, 22731, 42413, 24156, 125585, [458512]*4, 43171, 21972, 15109, 27392, 11683, 23364, 
                                                            [38184]*2, 85492, 12366, 23417, 24367, 54057, 36533, 22516, 23555, 11726, 5381, 15779]),
                                    'Total_m': flatten_list([21857, 32891, 16199, 35473, 20938, 133119, [479338]*4, 36495, 18115, 13137, 24104, 10456, 19706,
                                                            [29836]*2, 72839, 7338, 13636, 16962, 33387, 24513, 14760, 14313, 10148, 2843, 12476]),                                   
                                    'Provincias': provincias}),
                      how="outer")        
        pp['Total'] = pp['Total_v'] +pp['Total_m']        
        
        agg = [1,0]  
        # Moroni: 
        # estimación de totales de ñuble-1 (20290,20291) y ñuble-2 
        pp.loc[pp['Provincias'] == 'Nuble-1', 'Total'] = 20290
        pp.loc[pp['Provincias'] == 'Nuble-2', 'Total'] = 47730
        # para Santiago-4 el total está entre 87222 y 87232.
        
        # DATOS : Urzúa Valenzuela, p610.
        # HAY INCONSISTENCIAS EN EL ORDEN. Contraste con Moroni y Aldunate arroja los siguientes errores (los datos faltantes vienen de PDBA, de existir): 
        # PC : votación de Cautín va en Valdivia. Falta Coquimbo (13077, discrepancia 16.79 vs 16.99)
        # PS : Cautín, Valdivia y Osorno van uno más abajo.
        # PADENA : los datos de Linares, Ñuble y Concepción están corridos. Falta Santiago 1-2-3
        # PR : Falta Coquimbo (14565, discrepancia 18.7 vs 18.57)
        # DAL : los datos originales están corridos. Discrepancia en Atacama (según Moroni) o Coquimbo (PDBA/Urzua).
        # PDo : datos corridos. Falta Coquimbo (139, según Aldunate/PDBA), Moroni en cambio señala Atacama.
        # AN : Tarapacá va en Antofagasta.
        # CP : dato corrido, va en Linares en vez de Arauco.
        # VNP : 9,10,12 están bien posicionados. Los otros 2 están corridos linares en vez de concepción, cautín en vez de chiloé. Falta Valparaíso (1320) y Santiago (1913, agregado).
        # DC : falta la votacion de aysen (3072)
        # PL : en Colchagua hay discrepancia con Moroni (4.75), más no con Aldunate (11.17). El dato coincide con PDBA y el total de Wikipedia.
        # IND : Valparaíso discrepa con Moroni/Aldunate (0.48 vs 0.51)

        # VOTOS TOTALES : el total y la mayoría de los partidos coinciden con wikipedia, excepto 
        # - PC (290476 vs 290635), PR (313012 vs 312912) : al cambiar coquimbo (13077+159 y 14565-100, resp.) se ajustan las discrepancias antes mencionadas.
        # - IND (5589 vs 5669) : al cambiar valparaíso (1244+80) se ajusta la discrepancia
        # - PADENA (65479 vs 74583 = -9104) : santiago1-2-3, ojalá desagrupar
        # - VNP : coincide, pero santiago1-2-3-4 está agregado (de Cope : santiago-4 = 152, santiago1-2-3: 1913-152). No fue utilizado.
        
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
        pp.loc[pp['Partido'] == siglas['Vanguardia Nacional del Pueblo'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 1320, [1913,0,0,0], 541, 57, 0, 970, 0, 430,
                                                                                                [0]*2, 0, 0, 0, 0, 406, 0, 0, 0, 0, 0, 0])        

        pp.loc[pp['Partido'] == siglas['Independiente'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 1324, [0]*4, 0, 0, 0, 0, 0, 0,
                                                                               [0]*2, 0, 0, 0, 0, 0, 0, 4345, 0, 0, 0, 0])

    elif eleccion == 1961:
        # Aldunate p.213; p.215 y 219 totales varones y mujeres       
        pp = pd.merge(pd.DataFrame.from_records([(d,l,p) for d in provincias for p,l in pl], columns = ['Provincias', 'Lista/Pacto', 'Partido'] ),
                      pd.DataFrame({'Total': flatten_list([25293, 48198, 25446, 52967, 31280, 141396, [440477]*4, 57904, 33436, 20557, 37213, 18370, 32104,
                                                          [52015]*2, 101931, 16321, 25389, 31706, 59413, 41905, 24835, 25660, 17720, 4953, 19187]),
                                   # 'Total_v': flatten_list([17317, 32740, 16513, 32190, 19103, 88166, [268843]*4, 34886, 19623, 12250, 21758, 10374, 18609,
                                   #                          [32062]*2, 64324, 10990, 18253, 20510, 41630, 28194, 17045, 17371, 9756, 3348, 11530]),
                                   # 'Total_m': flatten_list([7976, 15458, 8933, 20777, 12177, 53230, [171634]*4, 23018, 13813, 8307, 15455, 7996, 13495,
                                   #                          [19953]*2, 37607, 5331, 7136,  11196, 17783, 13711, 7790, 8289, 7964, 1605, 7657]),
                                   'Provincias': provincias}),
                      how="outer")

        agg = [1,0]        
        
        # DATOS : Urzúa Valenzuela, p598.
        # PADENA : typo en Valparaíso (18673 en vez de 673)
        # CP, UNL, IND : obtenidos de PDBA
        
        # VOTOS TOTALES : difieren en 30 (1385646 vs 1385676), la comparación con el total de varones y mujeres arroja una diferencia en Coquimbo (+10, 52957) y Curicó (+20, 20537). Aysén y Chiloé están intercambiados. 
        # Los partidos coinciden,  excepto
        # - PC (156572 vs 157572) Diferencia en valdivia con pdba (3371 vs 4371), porcentaje coincide con Urzua, p600
        # - PCU (199260 vs 198260) Diferencia en antofagasta con pdba (3704 vs 2704).
        # (NOTA : en ambos casos, el porcentaje obtenido con el primer valor coincide con Aldunate)
        
        
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
        pp.loc[pp['Partido'] == siglas['Independiente'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [0]*4, 0, 0, 0, 0, 0, 0,
                                                                               [0]*2, 0, 0, 0, 2720, 0, 0, 0, 0, 0, 0, 0])
               
    elif eleccion == 1957:        
        # REVISAR
        
        # Aldunate, p. 211 
        # totales corresponden a «Válidamente emitidos»   
        # error en Colchagua : 37948 en vez de 22948 (lo cual coincide con el total de Nohlen y los porcentajes de Aldunate)
        pp = pd.merge(pd.DataFrame.from_records([(d,l,p) for d in provincias for p,l in pl], columns = ['Provincias', 'Lista/Pacto', 'Partido'] ),
                      pd.DataFrame({'Total': flatten_list([14817, 18305, 13068, 33079, 23440, 83389, [256853]*4, 34969, 22948, 14805, 29175, 14980, 27661,
                                                          [38770]*2, 60236, 9306, 19725, 24889, 46345, 30404, 17719, 17838, 12646, 2901, 9961]),
                                    'Provincias': provincias}),
                      how="outer")
        
        agg = [1,0]
        
        # notas : partido del trabajo (comunista), conservador unido (ex-tradicionalista), conservador (socialcristiano)
        
        # DATOS : urzua valenzuela, p579; comparados con totales de Nohlen.
        # MR: typo en Antogasta (1806 es 1086), valparaíso (2957 en vez de 2950, coincide con pdba, compensa total partido y total provincial)
        # PN : incompleto, obtenido de pdba (Coquimbo, curicó, arauco, llanquihue, chiloe). El valor de Santiago parece ser solo el primer distrito. 4437 (en vez de 3444) hace coincidir el total nacional (Nohlen). Urzua le llama «democrático nacional»
        # PDo : typo en Santiago-1 (11583 es 1583)
        # PDD: falta ñuble, malleco y Cautín (pdba). 
        # FN : typo en Talca (2586 en vez de 2486), que coincide con el porcentaje de Aldunate, compensa el total partido y provincial.
        # PRDo : falta Antofagasta (1)
        # PT : faltan Tarapaca, Antofagasta (359 en vez de 353, de modo que cuadre la región)
        # MONAP : 1342 según Nohlen, pero Urzua-Valenzuela incluye Santiago 2-3 :602 y 188.
        
        # socialistas : Santiago está agregado, no fue considerado que la suma de PDBA (27420=16314+10926) difiere en 181 de Urzua-Valenzuela (27239=9617+5236+10051+2335).        
        # PSP : falta Tarapacá (1685 en vez de 1691, de modo que cuadre la región), cautin = 2519+77, que cuadra la región y la suma socialista de Urzua.
        # PS : nuble=2036+52, que cuadran la región y la suma socialista de Urzua.

        # democráticos : al parecer Urzúa agrega ambos democráticos en Nuble, Malleco y Cautín
        # PDo : 44509 vs 44213 = +296
        # PDD : 3006 vs 3302 = -296 (PDBA incluye votos en Nuble, malleco y cautín : 26,137,145=308)
        
        # para conservadores : sería mejor revisar directamente el libro del servel
        
        # conservadores : Santiago está combinado, pero en el tercer y cuarto distrito solo hubo candidaturas PCU 
        # Comparacion con Nohlen desagregando por PDBA
        # PCU : 124119 vs 121223 = +2896
        # PCSC : 30506 vs 33654 = -3148        
        # esta diferencia se explica minimamente por la discrepancia de sumas en Valpo (16499 vs 16529 = -30), colchagua (10057 vs 10053 = +4), nuble (6095 vs 6338 = -243), malleco (1181 (167+1014) vs 1164 = +17). 
        # No es claro a quién agregarle estos valores (30-4+243-17 = 252). 
        # la hipótesis es que hay uno o más valores cambiados. Verificamos y descartamos las provincias con uno o ningún competidor
        # 1-Tarapacá, 2-Antofagasta, 3-Atacama, 18-Arauco, 21-Cautin, 22-valdivia
        # 23-osorno, 24-llanquihue, 25-castro, 26-magallanes (la candidata maría elena vukovic aparece como conservadora)

        # y aquellas en que uno de los partidos (mas no ambos) resultó electo : 
        # 4-Coquimbo, 5-aconcagua, 6-valpo,8-santiago,9-ohiggins,10-colchagua,12-talca,19-biobio        
        # quedan
        # 11-curico, 2626 (en 53 ganaron la diputacion, pcsc no se presentó)
        # 13-maule, -1375 (acá casi ganó el PCSC)
        # 14-linares, 1610 (linares PCU; 2232, pSCS 0)
        # 15-nuble, 1913 (53: PCU 4012 / PCSC 1941)
        # 17-conce, 4818 (53: PCU 4034/ PCSC 3050)
        # 20-malleco, 847 (53:PCU no compitio, PCSC saco 474)
        
   
        # PT : 17784 vs 17785 = -1
        # PR : 188527 vs 188526 = +1 (sobra 1 en santiago)

                
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
#                                                                                                 [26]*2, 0, 0, 0, 137, 145, 0, 0, 0, 0, 0, 0])  
        
        pp.loc[pp['Partido'] == siglas['Falange Nacional'],'Votos'] = flatten_list([1990, 2881, 3050, 1923, 1162, 4466, [16004,6099,11849,5032], 3104, 0, 0, 2486, 0, 2724,
                                                                                  [1897]*2, 4611, 0, 0, 0, 6994, 2038, 1294, 2058, 463, 585, 0])  
        pp.loc[pp['Partido'] == siglas['Partido Laborista'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [1873,3650,0,0], 0, 0, 32, 0, 0, 0,
                                                                                   [0]*2, 2455, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])  
        pp.loc[pp['Partido'] == siglas['Partido Liberal'],'Votos'] = flatten_list([2467, 2205, 3345, 9392, 6020, 8368, [13643,1414,11511,4166], 6780, 6071, 3019, 5439, 3396, 6961,
                                                                                 [5823]*2, 4276, 0, 2977, 7621, 4103, 8749, 3098, 1785, 1821, 291, 0])  
        pp.loc[pp['Partido'] == siglas['Movimiento Nacional del Pueblo'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [1342,0,0,0], 0, 0, 0, 0, 0, 0, #[0, 0, 0, 0, 0, 0, [1342,0,602,188], 0, 0, 0, 0, 0, 0,
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

        pp.loc[pp['Partido'] == siglas['Independiente'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 9443, [5248,0,0,0], 0, 0, 0, 0, 0, 0,
                                                                               [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2613]) 
        
    elif eleccion == 1953:   
        # REVISAR (error en 2 y 12)
              
        # Aldunate, p. 194  (los valores de Chiloé y Aysén están invertidos)
        pp = pd.merge(pd.DataFrame.from_records([(d,l,p) for d in provincias for p,l in pl], columns = ['Provincias', 'Lista/Pacto', 'Partido'] ),
                      pd.DataFrame({'Total': flatten_list([12884, 19346, 10437, 28380, 20302, 75165, [234607]*4, 32406, 20756, 12451, 25693, 14030, 24648,
                                                          [34062]*2, 52485, 8502, 16936, 20934, 41006, 26925, 15903, 15753, 11084, 2325, 9791]),
                                    'Provincias': provincias}),
                      how="outer")        
        
        # notas : conservador (socialcristiano), democratico (de chile)        
        pp.loc[pp['Partido'] == siglas['Acción Renovadora de Chile'],'Votos'] = flatten_list([0, 0, 0, 0, 13, 3094, [6373]*4, 0, 0, 0, 0, 0, 0,
                                                                                            [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido Agrario'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [144]*4, 0, 0, 336, 1, 0, 792,
                                                                                 [330]*2, 0, 0, 425, 1704, 2104, 0, 0, 0, 0, 0, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido Agrario Laborista'],'Votos'] = flatten_list([663, 1191, 0, 1185, 3403, 8415, [34144]*4, 4303, 1977, 2095, 10159, 3511, 7778,
                                                                                           [4627]*2, 4741, 0, 2596, 3235, 8882, 5798, 3209, 4935, 534, 818, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido Conservador Social Cristiano'],'Votos'] = flatten_list([0, 251, 0, 1197, 1699, 7167, [5446]*4, 621, 840, 0, 1779, 1679, 0,
                                                                                                      [1941]*2, 3050, 780, 0, 474, 412, 1447, 1552, 2271, 233, 308, 185]) 
        pp.loc[pp['Partido'] == siglas['Partido Conservador Tradicionalista'],'Votos'] = flatten_list([0, 376, 0, 59, 2458, 5156, [26491]*4, 6881, 8151, 1682, 5135, 73, 2232,
                                                                                                     [4012]*2, 4034, 1504, 1803, 0, 3385, 0, 77, 2483, 2297, 22, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido Democrático'],'Votos'] = flatten_list([0, 406, 0, 0, 13, 1129, [1029]*4, 0, 0, 0, 0, 0, 0,
                                                                                     [1181]*2, 2789, 12, 2238, 1006, 73, 1620, 0, 71, 0, 3, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido Democrático del Pueblo'],'Votos'] = flatten_list([119, 259, 0, 265, 0, 1694, [12000]*4, 0, 0, 405, 0, 4242, 0,
                                                                                                [1343]*2, 5302, 1444, 665, 55, 471, 2737, 344, 190, 174, 243, 0]) 
        pp.loc[pp['Partido'] == siglas['Falange Nacional'],'Votos'] = flatten_list([1906, 2003, 2009, 1130, 0, 942, [6851]*4, 2144, 0, 38, 618, 232, 310,
                                                                                  [0]*2, 11, 0, 399, 0, 1067, 1811, 25, 0, 757, 0, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido Laborista'],'Votos'] = flatten_list([0, 114, 0, 0, 0, 582, [5594]*4, 0, 0, 0, 0, 0, 0,
                                                                                   [0]*2, 1376, 0, 0, 0, 0, 505, 0, 0, 0, 0, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido Liberal'],'Votos'] = flatten_list([1949, 1903, 0, 8711, 3636, 6296, [14166]*4, 3963, 3647, 2558, 2757, 3276, 3569,
                                                                                 [4435]*2, 4858, 0, 1287, 5376, 2684, 4841, 3633, 462, 734, 0, 0]) 
        pp.loc[pp['Partido'] == siglas['Movimiento Nacional del Pueblo'],'Votos'] = flatten_list([60, 594, 0, 876, 0, 0, [12940]*4, 42, 265, 0, 0, 0, 0,
                                                                                                [356]*2, 2167, 0, 0, 0, 279, 306, 395, 0, 612, 0, 0]) 
        pp.loc[pp['Partido'] == siglas['Movimiento Nacional Ibañista'],'Votos'] = flatten_list([493, 985, 25, 268, 2182, 13108, [4890]*4, 1271, 0, 0, 0, 0, 0,
                                                                                              [1982]*2, 321, 24, 0, 4, 1101, 1768, 36, 477, 1, 16, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido Nacional Cristiano'],'Votos'] = flatten_list([0, 151, 0, 243, 0, 489, [10890]*4, 0, 1748, 0, 876, 0, 1393,
                                                                                            [831]*2, 168, 0, 0, 480, 4393, 133, 0, 0, 32, 0, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido Radical'],'Votos'] = flatten_list([2605, 3391, 3595, 6819, 2938, 9024, [20395]*4, 2571, 1126, 1841, 2167, 497, 3176,
                                                                                 [7142]*2, 7504, 891, 3864, 3244, 6345, 2788, 2485, 3009, 3021, 597, 2543])
        pp.loc[pp['Partido'] == siglas['Partido Radical Doctrinario'],'Votos'] = flatten_list([99, 275, 0, 148, 440, 1509, [9412]*4, 0, 0, 0, 776, 0, 0,
                                                                                             [639]*2, 0, 0, 1465, 1574, 1325, 608, 0, 0, 0, 0, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido Socialista'],'Votos'] = flatten_list([2641, 4663, 0, 1464, 610, 3864, [19688]*4, 1473, 758, 185, 576, 0, 114,
                                                                                    [1498]*2, 4561, 698, 248, 0, 0, 608, 234, 129, 55, 54, 89])
        pp.loc[pp['Partido'] == siglas['Partido Socialista Popular'],'Votos'] = flatten_list([1312, 11600, 2260, 4071, 1508, 4456, [14422]*4, 821, 995, 2694, 1127, 513, 2453,
                                                                                            [2664]*2, 8091, 772, 1860, 2745, 1895, 1042, 1642, 788, 2172, 215, 3845]) 
        pp.loc[pp['Partido'] == siglas['Unión Nacional de Independientes'],'Votos'] = flatten_list([410, 659, 2443, 1728, 1266, 1424, [13641]*4, 7848, 1162, 0, 0, 0, 0,
                                                                                                  [2]*2, 3088, 443, 0, 26, 3540, 17, 2074, 8, 96, 2, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido Unidad Popular'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [420]*4, 0, 0, 0, 0, 0, 0,
                                                                                        [0]*2, 0, 1900, 0, 0, 0, 0, 0, 0, 0, 0, 24]) 

        # # partido progresista femenino
        # pp.loc[pp['Partido'] == partido[4],'Votos'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        # # partido femenino
        # pp.loc[pp['Partido'] == partido[13],'Votos'] = [0]*29 
        # # union nacional de jubilados
        # pp.loc[pp['Partido'] == partido[20],'Votos'] = [0]*29 
        # democratico nacional
        #v.loc[pp['Partido'] == partido[21],'Votos'] = [0]*29 
        # # nueva accion publica
        # pp.loc[pp['Partido'] == partido[23],'Votos'] = [0]*29 
        # # comerciantes frutos del país
        # pp.loc[pp['Partido'] == partido[24],'Votos'] = [0]*29 
        # # organizacion campesina
        # pp.loc[pp['Partido'] == partido[25],'Votos'] = [0]*29 
        # # movimiento socialcristiano
        # pp.loc[pp['Partido'] == partido[26],'Votos'] = [0]*29 
        # # partido nacional araucano
        # pp.loc[pp['Partido'] == partido[27],'Votos'] = [0]*29 
        # # independientes
        # pp.loc[pp['Partido'] == partido[28],'Votos'] = [0]*29 

    elif eleccion == 1949:         
        # REVISAR (error en 8, 14, 15, 20)
            
        # Aldunate, p.192
        pp = pd.merge(pd.DataFrame.from_records([(d,l,p) for d in provincias for p,l in pl], columns = ['Provincias', 'Lista/Pacto', 'Partido'] ),
                      pd.DataFrame({'Total': flatten_list([9753, 12625, 7287, 16147, 11888, 45387, [123078]*4, 19461, 11630, 6974, 14241, 7755, 12410,
                                                          [20332]*2, 30787, 6012, 12407, 13878, 28673, 18738, 10911, 11308, 6970, 1031, 5470]),
                                    'Provincias': provincias}),
                      how="outer")

        # notas : conservador (socialcristiano)        
        pp.loc[pp['Partido'] == siglas['Acción Renovadora de Chile'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [1985]*4, 0, 0, 0, 0, 0, 0,
                                                                                            [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        pp.loc[pp['Partido'] == siglas['Partido Agrario Laborista'],'Votos'] = flatten_list([12, 0, 0, 1, 184, 1606, [12126]*4, 2493, 0, 1077, 2374, 1205, 1938,
                                                                                           [1432]*2, 619, 0, 1821, 1734, 5544, 1947, 1100, 1395, 0, 138, 0])
        pp.loc[pp['Partido'] == siglas['Partido Conservador Social Cristiano'],'Votos'] = flatten_list([0, 811, 1645, 2151, 3018, 10952, [31600]*4, 7596, 4981, 1591, 3811, 0, 2926,
                                                                                                      [2681]*2, 6295, 1530, 1686, 1104, 5638, 1086, 1800, 3485, 1544, 34, 153]) 
        pp.loc[pp['Partido'] == siglas['Partido Conservador Tradicionalista'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [3846]*4, 0, 0, 0, 0, 0, 0,
                                                                                                     [3739]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])  
        pp.loc[pp['Partido'] == siglas['Partido Demócrata'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [1994]*4, 0, 0, 0, 0, 0, 0,
                                                                                   [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])    
        pp.loc[pp['Partido'] == siglas['Partido Democrático'],'Votos'] = flatten_list([0, 1376, 37, 83, 182, 2136, [5285]*4, 9, 0, 69, 122, 84, 1,
                                                                                     [686]*2, 3705, 875, 705, 1083, 2017, 2155, 0, 69, 0, 0, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido Democrático del Pueblo'],'Votos'] = flatten_list([1446, 704, 0, 0, 0, 633, [3281]*4, 0, 0, 0, 15, 0, 0,
                                                                                                [92]*2, 1744, 0, 93, 0, 320, 118, 0, 55, 0, 31, 0])
        pp.loc[pp['Partido'] == siglas['Falange Nacional'],'Votos'] = flatten_list([1392, 1771, 1005, 916, 441, 1075, [4582]*4, 1507, 0, 0, 482, 205, 371,
                                                                                  [235]*2, 992, 0, 827, 266, 687, 962, 0, 0, 493, 0, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido Laborista'],'Votos'] = flatten_list([0, 104, 0, 0, 0, 15, [4050]*4, 0, 0, 0, 5, 0, 2,
                                                                                   [0]*2, 2, 382, 2, 0, 2, 541, 0, 0, 0, 0, 0])        
        pp.loc[pp['Partido'] == siglas['Partido Liberal'],'Votos'] = flatten_list([2371, 1932, 0, 5393, 4439, 7663, [17831]*4, 2612, 3500, 1723, 3763, 2567, 4294,
                                                                                 [1447]*2, 4899, 0, 1842, 2681, 3661, 5047, 1603, 2281, 1801, 230, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido Liberal Progresista'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [0]*4, 0, 0, 0, 0, 0, 0,
                                                                                             [0]*2, 0, 0, 983, 2629, 2819, 0, 0, 0, 0, 0, 0])    
        pp.loc[pp['Partido'] == siglas['Movimiento Social Cristiano'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [489]*4, 0, 0, 0, 0, 1529, 0,
                                                                                             [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])    
        pp.loc[pp['Partido'] == siglas['Partido Radical'],'Votos'] = flatten_list([2368, 3714, 3608, 5111, 2834, 9598, [19022]*4, 2265, 2010, 1952, 2308, 1714, 2492,
                                                                                 [8598]*2, 8669, 2123, 1887, 2007, 3192, 3969, 3778, 2683, 2028, 461, 2488])
        pp.loc[pp['Partido'] == siglas['Partido Radical Democrático'],'Votos'] = flatten_list([1344, 269, 0, 424, 0, 1677, [3080]*4, 722, 866, 229, 93, 451, 270,
                                                                                             [899]*2, 1070, 600, 1718, 1533, 2214, 1753, 1678, 1143, 1076, 90, 0])
        pp.loc[pp['Partido'] == siglas['Partido Radical Doctrinario'],'Votos'] = flatten_list([56, 0, 0, 0, 0, 334, [1857]*4, 0, 0, 0, 0, 0, 0,
                                                                                             [0]*2, 0, 0, 0, 404, 1818, 0, 0, 0, 0, 0, 0])
        pp.loc[pp['Partido'] == siglas['Partido Socialista'],'Votos'] = flatten_list([282, 554, 79, 495, 146, 2074, [7230]*4, 1132, 94, 0, 35, 0, 18,
                                                                                    [190]*2, 1731, 0, 405, 0, 139, 722, 14, 0, 0, 0, 0])        
        pp.loc[pp['Partido'] == siglas['Partido Socialista Popular'],'Votos'] =  flatten_list([475, 536, 714, 1055, 644, 1387, [8017]*4, 1125, 179, 22, 864, 0, 103,
                                                                                             [523]*2, 941, 502, 433, 110, 605, 437, 849, 85, 0, 35, 2780]) 
        pp.loc[pp['Partido'] == siglas['Partido Socialista Auténtico'],'Votos'] = flatten_list([0, 852, 199, 517, 0, 397, [2413]*4, 0, 0, 0, 369, 0, 0,
                                                                                              [0]*2, 28, 0, 0, 334, 7, 0, 0, 0, 0, 0, 0])
        # pp.loc[pp['Partido'] == siglas['Independiente'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        #                                                                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]            

    elif eleccion == 1945:    
        # REVISAR (solo faltan totales por santiago y nuble, toda la info esta desagregada)
        
        # Aldunate, p.179
        pp = pd.merge(pd.DataFrame.from_records([(d,l,p) for d in provincias for p,l in pl], columns = ['Provincias', 'Lista/Pacto', 'Partido'] ),
                      pd.DataFrame({'Total': flatten_list([9371, 15082, 5224, 19298, 12460, 45087, [59126,17785,23645,15719], 17507, 12561, 7651, 14556, 6511, 13260,
                                                          [6807,13380], 28695, 5718, 12125, 13819, 24882, 17447, 9722, 10046, 6259, 976, 5211]),
                                    'Provincias': provincias}),
                      how="outer")
        
        # DATOS : Urzúa-Valenzuela, p.538      
        # notas : 'Progresista Nacional (comunistas)
        
        # total : 449930 vs 449916 nohlen
        # revisar nuble : a falta de evidencia cambio los totales : 6923-116, 13264+116
        # PL : 80577 vs 80597 (typo en nohlen, +20 en linares coincidente con pdba)
        # pdo : 21462 vs 21463 (+1 en nuble)
        # ind 4025 vs 4029 ?
        # plp : 9849 vs ?
        # pdn : 2565 vs ?
        # pla 130 ?

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
                                                                                   [0,0], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])        
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
        pp.loc[pp['Partido'] == siglas['Independiente'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 1367, [0]*4, 0, 0, 0, 0, 0, 0,
                                                                               [0]*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2658])     
                
    elif eleccion == 1941:    
        # REVISAR

        # Aldunate, p.177
        pp = pd.merge(pd.DataFrame.from_records([(d,l,p) for d in provincias for p,l in pl], columns = ['Provincias', 'Lista/Pacto', 'Partido'] ),
                      pd.DataFrame({'Total': flatten_list([11614, 18165, 7917, 19812, 12137, 43283, [113196]*4, 18974, 12184, 7247, 13661, 7026, 12065,
                                                          [21275]*2, 28661, 5380, 12290, 13980, 25571, 15770, 8702, 9115, 5960, 937, 5416]),
                                    'Provincias': provincias}),
                      how="outer")

        # notas : 'Progresista Nacional (comunistas)

        pp.loc[pp['Partido'] == siglas['Partido Agrario'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 0, [0]*4, 0, 0, 0, 993, 0, 1522,
                                                                                 [1078]*2, 0, 313, 0, 0, 3817, 0, 0, 0, 0, 0, 0])
        pp.loc[pp['Partido'] == siglas['Alianza Popular Libertadora'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 714, [260]*4, 0, 0, 0, 488, 0, 0,
                                                                                             [0]*2, 4, 0, 0, 0, 0, 488, 799, 0, 0, 0, 0])
        pp.loc[pp['Partido'] == siglas['Partido Conservador'],'Votos'] = flatten_list([14, 1514, 938, 1481, 2344, 7724, [23020]*4, 4644, 3466, 1702, 3645, 1500, 2997,
                                                                                     [6121]*2, 3500, 0, 2595, 1575, 2471, 517, 952, 2981, 1537, 66, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido Demócrata'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 436, [246]*4, 39, 248, 38, 0, 0, 25,
                                                                                   [0]*2, 2919, 0, 72, 1007, 1333, 0, 0, 0, 0, 0, 0])
        pp.loc[pp['Partido'] == siglas['Partido Democrático'],'Votos'] = flatten_list([0, 903, 0, 310, 32, 942, [8395]*4, 35, 90, 368, 215, 208, 589,
                                                                                     [7451]*2, 1315, 9, 1135, 826, 1637, 981, 170, 115, 148, 27, 0])
        pp.loc[pp['Partido'] == siglas['Falange Nacional'],'Votos'] = flatten_list([1904, 1557, 0, 796, 84, 2942, [4475]*4, 907, 0, 0, 445, 112, 449,
                                                                                  [127]*2, 566, 0, 274, 0, 726, 0, 0, 0, 159, 0, 0])    
        pp.loc[pp['Partido'] == siglas['Partido Liberal'],'Votos'] = flatten_list([1479, 213, 624, 4142, 2956, 7198, [11196]*4, 3222, 2228, 1614, 1891, 2323, 1771,
                                                                                 [3160]*2, 1524, 592, 2338, 3612, 3683, 2136, 948, 1058, 1041, 47, 0]) 
        pp.loc[pp['Partido'] == siglas['Partido Progresista Nacional'],'Votos'] = flatten_list([3700, 7514, 0, 4136, 1825, 5466, [12397]*4, 2690, 373, 1218, 1797, 0, 0,
                                                                                              [784]*2, 5773, 1880, 0, 671, 1078, 1365, 186, 155, 0, 34, 0])
        pp.loc[pp['Partido'] == siglas['Partido Radical'],'Votos'] = flatten_list([2206, 3160, 4360, 5729, 2750, 7135, [16790]*4, 2836, 1896, 1368, 1987, 2407, 2197,
                                                                                 [5575]*2, 6252, 1599, 3768, 4006, 6313, 3481, 1475, 1448, 2230, 2041, 2041])
        pp.loc[pp['Partido'] == siglas['Partido Radical Socialista'],'Votos'] = flatten_list([0, 0, 0, 0, 0, 381, [3575]*4, 0, 0, 0, 0, 74, 12,
                                                                                            [1000]*2, 0, 0, 0, 0, 13, 0, 0, 0, 0, 0, 0])
        pp.loc[pp['Partido'] == siglas['Partido Socialista'],'Votos'] = flatten_list([1847, 2855, 1684, 2910, 2146, 7928, [20999]*4, 3379, 3409, 936, 1709, 401, 2049,
                                                                                    [2365]*2, 2687, 987, 2108, 1689, 3620, 4111, 3672, 3358, 845, 2316, 2316])    
        pp.loc[pp['Partido'] == siglas['Partido Socialista de Trabajadores'],'Votos'] = flatten_list([396, 449, 311, 308, 0, 924, [4317]*4, 947, 117, 0, 123, 0, 454,
                                                                                                    [380]*2, 3368, 0, 0, 0, 54, 313, 75, 0, 0, 0, 0])
        pp.loc[pp['Partido'] == siglas['Vanguardia Popular Socialista'],'Votos'] = flatten_list([68, 0, 0, 0, 0, 1447, [5906]*4, 269, 0, 0, 368, 0, 0,
                                                                                               [0]*2, 753, 0, 0, 474, 820, 745, 325, 0, 0, 0, 0])        
        # # laborista
        # pp.loc[pp['Partido'] == partido[13],'Votos'] = [0]*29
        # # laborista proletario
        # pp.loc[pp['Partido'] == partido[14],'Votos'] = [0]*29
        # # radical socialista obrero
        # pp.loc[pp['Partido'] == partido[15],'Votos'] = [0]*29
        # # regionalista de magallanes
        # pp.loc[pp['Partido'] == partido[16],'Votos'] = [0]*29        
        # # independientes
        # pp.loc[pp['Partido'] == partido[17],'Votos'] = [0]*29 
        
    else:
        Exception()
        # pp.loc[pp['Partido'] == siglas[''],'Votos'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        #                                                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]          

    # if True:
    #     print(v.groupby(['Provincias']).agg({'Votos':'sum'}))

    ## los datos de santiago (71,72,73,8) y nuble (15,16) vienen por agrupacion departamental, pero los totales son provinciales    
    if agg[0] == 1:
        aux = pp[(pp['Provincias'].str.contains('Santiago')) & (pp['Partido'] != '')].groupby(['Lista/Pacto', 'Partido']).agg({'Votos':'sum'}).reset_index()   
        pp.loc[(pp['Provincias'] == 'Santiago-1') & (pp['Partido'] != ''), aux.columns.tolist()] = aux.loc[:, aux.columns.tolist()].values
        pp.loc[(pp['Provincias'] == 'Santiago-2') & (pp['Partido'] != ''), aux.columns.tolist()] = aux.loc[:, aux.columns.tolist()].values
        pp.loc[(pp['Provincias'] == 'Santiago-3') & (pp['Partido'] != ''), aux.columns.tolist()] = aux.loc[:, aux.columns.tolist()].values
        pp.loc[(pp['Provincias'] == 'Santiago-4') & (pp['Partido'] != ''), aux.columns.tolist()] = aux.loc[:, aux.columns.tolist()].values   
      
    if agg[1] == 1:
        aux = pp[pp['Provincias'].str.contains('Nuble')].groupby(['Lista/Pacto', 'Partido']).agg({'Votos':'sum'}).reset_index()   
        pp.loc[pp['Provincias'] == 'Nuble-1', aux.columns.tolist()] = aux.loc[:, aux.columns.tolist()].values
        pp.loc[pp['Provincias'] == 'Nuble-2', aux.columns.tolist()] = aux.loc[:, aux.columns.tolist()].values

    ## las provincias de Llanquihue y Aysen forman una agrupación departamental
    if eleccion <= 1965:
        pp['Provincias'] = pp['Provincias'].replace({'Llanquihue':'Llanquihue-Aysén', 'Aysén':'Llanquihue-Aysén'})
        pp = pp.groupby(['Provincias', 'Lista/Pacto', 'Partido']).sum().reset_index()

        provincias.remove('Aysén') 
        provincias[-3] = 'Llanquihue-Aysén'           

    # estadística    
    pp.loc[pp['Lista/Pacto'] == 'Válidamente emitidos','Votos'] = pp.groupby(['Provincias'], sort=False).agg({'Votos':'sum'}).values        
    pp.loc[pp['Lista/Pacto'] == 'Total','Votos'] = pp[pp['Lista/Pacto'] == 'Total']['Total']
    pp.loc[pp['Lista/Pacto'] == 'Blancos/Nulos','Votos'] = pp[pp['Lista/Pacto'] == 'Total']['Votos'].values - pp[pp['Lista/Pacto'] == 'Válidamente emitidos']['Votos'].values
         
    # reemplazar provincias por distrito numerado
    pp['Distrito'] = pp['Provincias'].replace(dict(zip(provincias, reg)) )
      
    # calcular porcentajes
    pp['Porcentaje'] = (100*pp['Votos']/pp['Total']).round(2)

    # agregar electos
    pp = pd.merge(pp,
                  pd.concat([candidatos[(candidatos['Lista/Pacto'] != 'Candidatura Independiente') & (candidatos['Partido'] == 'IND')].groupby([subdivrow, 'Lista/Pacto']).agg({'Partido':'first', 'Electos':'count'}).reset_index(),
                            candidatos[candidatos['Partido'] != 'IND'].groupby([subdivrow, 'Partido']).agg({'Lista/Pacto':'first', 'Electos':'count'}).reset_index(),
                            candidatos[candidatos['Lista/Pacto'] == 'Candidatura Independiente']
                            ])[['Distrito','Partido','Electos']],
                  how="outer").fillna(0)
    pp['Electos'] = pp['Electos'].map(lambda x: 1 if x == '*'else x).astype(int)        
          
    return pp[['Distrito', 'Lista/Pacto', 'Partido', 'Electos', 'Porcentaje', 'Votos']]
        
#%%
def Senado1989_presente(path_datos, candidatos, eleccion):
    """
    Adjunta los senadores en ejercicio al listado de candidatos. 
    
    Parametros
    ----------
    path_datos : PosixPath
        Directorio.
    candidatos : dataframe
        Candidatos a senador en cada circunscripción.
    eleccion : int
        Año de la elección.

    Returns
    -------
    candidatos : dataframe
        Candidatos y senadores en ejercicio.

    """
    from ast import literal_eval
        
    if candidatos.index.levels[1].dtype.name == 'category':
        candidatos.index.set_levels(
            candidatos.index.levels[1].astype(object),
            level='Lista/Pacto',
            inplace=True)        
    
    path_datos_prev = path_datos.parents[0]/str(eleccion-4)
    datos_filenames = sorted(path_datos_prev.glob('*Circunscripcion*_electos.csv'))

    pactos = pactos_electorales(eleccion)            
            
    if datos_filenames:
        electos_prev = pd.read_csv(datos_filenames[0]) 
        
        if eleccion == 1993: 
            electos_prev = electos_prev[~electos_prev['Circunscripción'].isin([1,3,5,6,10,11,14,15,18])]
        
        # cambios en militancia de un período a otro
        if eleccion == 2017:
            electos_prev.loc[electos_prev['Candidatos'].str.contains("Araya"),'Partido'] = 'PDC'
            electos_prev.loc[electos_prev['Candidatos'].str.contains("Guillier"),'Partido'] = 'PR'
            electos_prev.loc[electos_prev['Partido'] == "MAS",'Partido'] = 'PAIS'
        elif eleccion == 2013: 
            electos_prev.loc[electos_prev['Candidatos'].str.contains("Pérez"), 'Partido'] = 'IND'            
            electos_prev.loc[electos_prev['Candidatos'].str.contains("Horvath"), 'Partido'] = 'IND'
        elif eleccion == 2009:
            electos_prev.loc[electos_prev['Candidatos'].str.contains("Navarro"), 'Partido'] = 'MAS'
            electos_prev.loc[electos_prev['Candidatos'].str.contains("Cantero"), 'Partido'] = 'IND'            
        elif eleccion == 2005:
            electos_prev.loc[electos_prev['Candidatos'].str.contains("Horvath"), 'Partido'] = 'RN'
            electos_prev.loc[electos_prev['Candidatos'].str.contains("Arancibia"), 'Partido'] = 'UDI' 
            electos_prev.loc[electos_prev['Candidatos'].str.contains("Avila"), 'Partido'] = 'PRSD'
            electos_prev.loc[electos_prev['Candidatos'].str.contains("Lavandero"),
                            [ 'Partido','Candidatos','Votos','Porcentaje','url']] = ['PRSD', "['Guillermo', 'Vásquez', 'Úbeda']",'','','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Guillermo_V%C3%A1squez_Ubeda']
        elif eleccion == 2001: 
            electos_prev.loc[electos_prev['Partido'].str.contains("IND"), 'Partido'] = 'UDI'
        elif eleccion == 1993:
            electos_prev.loc[electos_prev['Candidatos'] == "['Eduardo', 'Frei', 'Ruiz-Tagle']",
                            [ 'Partido','Candidatos','Votos','Porcentaje', 'url']] = ['PS', "['María', 'Elena', 'Carrera', 'Villavicencio']",'','','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/María_Elena_Carrera_Villavicencio']
            electos_prev.loc[electos_prev['Candidatos'] == "['Jaime', 'Guzmán', 'Errázuriz']",
                            [ 'Partido','Candidatos','Votos','Porcentaje','url']] = ['RN', "['Miguel', 'Otero', 'Lathrop']",'','','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Jorge_Miguel_Otero_Lathrop']
            electos_prev.loc[electos_prev['Candidatos'].str.contains("Sule"), 'Partido'] = 'PR'
            electos_prev.loc[electos_prev['Candidatos'].str.contains("Cooper"),'Partido'] = 'RN'
            electos_prev.loc[electos_prev['Candidatos'].str.contains("Calderón"),'Partido'] = 'PS'

        # redistritaje 2017
        if eleccion == 2017:
            electos_prev['Circunscripción'] = [3,3,5,5,7,7,7,7,8,8,10,10,10,10,12,12,13,13,15,15]

        # ajustar pactos                
        prev_IND = {}        
        for partido in set(electos_prev[electos_prev['Partido'] != 'IND']['Partido']):
            if partido in pactos.keys():
                prev_IND[electos_prev[electos_prev['Partido'] == partido]['Lista/Pacto'].values[0]] = pactos[partido]
                electos_prev.loc[electos_prev['Partido'] == partido,'Lista/Pacto'] = pactos[partido]
        #problema : si un partido se sale de un pacto y hay IND
        electos_prev = electos_prev.replace({'Lista/Pacto':prev_IND}) 
                    
        # circ 100: senadores del período anterior
        # electos_prev['Circunscripción'] = 100    
        electos_prev['Candidatos'] = electos_prev['Candidatos'].apply(lambda x : literal_eval(str(x)))            
        electos_prev['Votos'] = 0   
        electos_prev['Porcentaje'] = 0
        electos_prev['Electos'] = '*'
                
        electos_prev = electos_prev.set_index(['Circunscripción','Lista/Pacto','Partido'])    
    
    # Vitalicios y designados : https://es.wikipedia.org/wiki/Anexo:Senadores_designados_de_Chile
    if eleccion <= 2001:             
        if eleccion <= 1993:
            designados = [['SUPREMA','Ricardo Martin Díaz'],
                          ['SUPREMA','Carlos Letelier Bobadilla'],
                          ['COSENA','Santiago Sinclair Oyaneder'],
                          ['COSENA','Ronald Mc-Intyre Mendoza'],
                          ['COSENA','Vicente Huerta Celis'],
                          ['SUPREMA','Olga Feliú Segovia'],
                          ['RN','William Thayer Arteaga'],      #GOB-RN
                          ['UDI','Sergio Fernández Fernández']] #GOB-UDI
            if (eleccion == 1989): designados += [['COSENA','César Ruiz Danyau']]           
        else:
            designados = [['SUPREMA', 'Marcos Aburto Ochoa'],
                          ['SUPREMA', 'Enrique Zurita Campos'],
                          ['COSENA', 'Julio Canessa Robert'],
                          ['COSENA', 'Jorge Martínez Busch'],
                          ['COSENA', 'Ramón Vega Hidalgo'],
                          ['COSENA', 'Fernando Cordero Rusque'],
                          ['PR', 'Enrique Silva Cimma'],        #CS-PR
                          ['PR', 'Augusto Parra Muñoz'],        #GOB-PR
                          ['PDC', 'Edgardo Böeninger Kausel'],  #GOB-DC
                          ['PDC', 'Eduardo Frei Ruiz-Tagle'],   #VIT-DC
                          ['VIT', 'Augusto Pinochet Ugarte']]
                         
        designados = pd.DataFrame.from_records(designados, columns=['Partido','Candidatos'])
        designados['Candidatos'] = nombres_formato(designados)
        
        # circ 101: designados y vitalicios
        designados['Circunscripción'] = 101         
        designados['Lista/Pacto']  = pactos['UDI']

        if eleccion >= 1997 :
            designados.loc[[False]*6+[True]*4+[False],'Lista/Pacto'] = pactos['PDC']

        designados = designados.set_index(['Circunscripción','Lista/Pacto','Partido'])        
        designados['Votos'] = 0
        designados['Porcentaje'] = 0
        designados['Electos'] = '*'
        designados['url'] = ''
        

        if eleccion == 1989:
            candidatos = pd.concat([candidatos, designados], axis=0)  
        else:
            candidatos = pd.concat([candidatos, electos_prev, designados], axis=0)              
    elif datos_filenames:    
        candidatos = pd.concat([candidatos, electos_prev], axis=0)
    
    return candidatos[['Candidatos', 'Votos', 'Porcentaje','Electos','url']]