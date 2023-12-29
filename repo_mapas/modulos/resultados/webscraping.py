#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 00:06:16 2023

@author: sebastian
"""
from unidecode import unidecode

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

import re
from operator import itemgetter

#%%
def url_parlamentarios(eleccion, rep):
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
                       str(eleccion),'-05-21' if (eleccion >= 1937 or eleccion == 1930) else ('-12-19' if eleccion == 1932 else ('-12-23' if rep == 0 else '-12-12')),'&fin=',
                       str(eleccion+4) if (eleccion >= 1937) else (str(eleccion+2) if eleccion == 1930 else str(eleccion+5)),
                       '-05-20' if (eleccion != 1930) else '-06-06',                           
                       '&periodo=1925-1973&cam=','Diputados' if rep == 0 else 'Senado'])   

    elif eleccion >= 1891: 
        url = ''.join(['https://www.bcn.cl/historiapolitica/corporaciones/periodo_detalle?inicio=',
                       str(eleccion),'-06-01' if (eleccion >= 1894) else '-12-26','&fin=',
                       str(eleccion+3) if eleccion < 1924 else '1924',
                       '-05-31' if eleccion < 1924 else '-09-11',                  
                       '&periodo=1891-1925&cam=','Diputados' if rep == 0 else 'Senado'])               

    elif eleccion >= 1834: 
        url = ''.join(['https://www.bcn.cl/historiapolitica/corporaciones/periodo_detalle?inicio=',
                       str(eleccion),'-06-01','&fin=',
                       str(eleccion+3), '-05-31' if eleccion < 1888 else '-02-11',                  
                       '&periodo=1833-1891&cam=','Diputados' if rep == 0 else 'Senado'])
    elif eleccion >= 1828:
        url = ''.join(['https://www.bcn.cl/historiapolitica/corporaciones/periodo_detalle?inicio=',
                       '1828-08-06&fin=1829-01-31' if eleccion == 1828 else ('1829-08-01&fin=1829-11-06' if eleccion == 1829 else '1831-06-01&fin=1833-05-24'),
                       '&periodo=1823-1833&cam=','Diputados' if rep == 0 else 'Senado'])

    return url    

#%%
def webscraping_parlamentarios(eleccion, rep):
    subdivrow = {0:'Distrito', 1:'Circunscripción'}[rep]

    ## iniciar selenium en Chrome   
    chrome_service = Service('/usr/bin/chromedriver')
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--headless') 
    
    driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
    url = url_parlamentarios(eleccion, rep)
    driver.get(url)
    
    # extraer 
    html = driver.page_source
    soup = BeautifulSoup(html,'html.parser')

    output_tbody = []
    
    if eleccion >= 1989:
        header = [subdivrow,'Lista/Pacto','Candidatos', 'Partido', 'Votos', 'Porcentaje', 'Electos']

        ## Distritos o circunscripciones por elección
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
            
            if eleccion >= 1891:
                try:
                    localidad, partido = itemgetter(2,4)(list(list_html[i].small.stripped_strings))
                except IndexError:
                    localidad, partido = list(list_html[i].small.stripped_strings)[2], ''
                    
                output_tbody.append([re.sub(r'\ ".*?\"', '', localidad).replace(' Agrupación Departamental','').replace(' Distrito','').lower(), None, page_id.replace("_"," "), partido, "", "", "*", "*", url])
            else:
                try:
                    cargo, localidad, partido = itemgetter(0,2,4)(list(list_html[i].small.stripped_strings))
                except IndexError:
                    cargo, localidad, partido = list(list_html[i].small.stripped_strings)[0], list(list_html[i].small.stripped_strings)[2], ''

                if ('Suplente' in cargo) or ('Subrogante' in cargo):
                    output_tbody.append([re.sub(r'\ ".*?\"', '', localidad).replace(' Agrupación Departamental','').replace(' Distrito',''), None, page_id.replace("_"," "), partido, "", "", " ", "*", url])                    
                elif (rep == 0 and 'Propietario' in cargo) or (rep == 1):
                    output_tbody.append([re.sub(r'\ ".*?\"', '', localidad).replace(' Agrupación Departamental','').replace(' Distrito',''), None, page_id.replace("_"," "), partido, "", "", "*", "*", url])
                # if ('Suplente' in cargo) or ('Subrogante' in cargo):
                #     output_tbody.append([re.sub(r'\ ".*?\"', '', localidad).replace(' Agrupación Departamental','').replace(' Distrito','').lower(), None, page_id.replace("_"," "), partido, "", "", " ", "*", url])                    
                # elif (rep == 0 and 'Propietario' in cargo) or (rep == 1):
                #     output_tbody.append([re.sub(r'\ ".*?\"', '', localidad).replace(' Agrupación Departamental','').replace(' Distrito','').lower(), None, page_id.replace("_"," "), partido, "", "", "*", "*", url])

        candidatos = pd.DataFrame.from_records(output_tbody, columns = header)

        if eleccion >= 1925:
            agrupaciones_dep = {'prim': '1', 'seg': '2', 'ter': '3', 'cuar': '4', 
                                'qui': '5', 'sex': '6', 'sép': '7', 'oct': '8', 'nov': '9', 
                                'dec':'1', 'duodéc':'12', 'déc': '10', 'undéc':'11', 'vige':'2', 'vigé':'20'}
    
            numeros = re.compile("|".join(agrupaciones_dep))            
            candidatos[subdivrow] = candidatos[subdivrow].map(lambda y: "".join(agrupaciones_dep[w] for w in numeros.findall(y)) if eleccion >= 1925 else agrupaciones_dep[numeros.search(y)[0]] )

        # if len(candidatos[candidatos[subdivrow]=='']) > 0:
        #     candidatos.loc[candidatos[subdivrow]=='', subdivrow] = '0'
        
    return candidatos

#%%
def biografiasBCN(eleccion, rep, electos):
    """
    Webscraping de biografías parlamentarias (1973-presente) desde la BCN.

    Parámetros
    ----------
    electos : dataframe
        Información de candidatos electos.

    Entrega
    -------
    electos : dataframe
        El dataframe original tiene una columna suplementaria, url, con las 
        biografías de cada candidato.
    """
    subdivrow = {0:'Distrito',1:'Circunscripción'}[rep]
    
    if not 'url' in electos.columns:
        electos['url'] = ''
     
    url_mask = (electos['url'].str.contains('bcn') == False) & ((electos['Electos'] == '*') | (electos['Electos_comp'] == '*')) &\
                ((~electos.index.get_level_values(0).isin(['Designados'])) if subdivrow in electos.index.names else (~electos[subdivrow].isin(['Designados'])))
                
    if (url_mask.sum() == 0):
        return None
    
    ## WEBSCRAPING
    print(electos.loc[url_mask]['Candidatos'])    
    
    # iniciar selenium en Chrome   
    chrome_service = Service('/usr/bin/chromedriver')
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--headless') 
    
    driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
    if eleccion >= 1989:
        driver.get('https://www.bcn.cl/historiapolitica/resenas_parlamentarias/index.html?categ=por_periodo&periodo=1990-2018')
    else:
        driver.get('https://www.bcn.cl/historiapolitica/resenas_parlamentarias/index.html?categ=por_periodo&periodo=1925-1973')
        
    elem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'busca_parlamentario')))        
    
    url = []
    
    for item in electos.loc[url_mask]['Candidatos']:    
        url_item = []
        i = 0
        
        while(not url_item and i < 3):
            if i == 0:
                search = (item[-2]+' '+item[-1])
            elif i == 1:
                search = (item[-2])
            elif i == 2:
                search = (item[-1])        

            elem.send_keys(search)    
            time.sleep(0.1*i)
    
            html = driver.page_source
            soup = BeautifulSoup(html,'html.parser')      
            listaBCN = soup.find(id='lista-busca-parla')    
            
            i += 1
            elem.clear()
    
            #Viera-Gallo, Jocelyn-Holt y Cruz-Coke no aparecen en BCN
            if (listaBCN is None) and ('-' in search):
                search = search.replace('-',' ')

                elem.send_keys(search)    
                time.sleep(0.1*i)
        
                html = driver.page_source
                soup = BeautifulSoup(html,'html.parser')      
                listaBCN = soup.find(id='lista-busca-parla')        
                elem.clear()    

            if listaBCN is None:
                continue
            else:
                div = listaBCN.find_all('a',href=True)
    
            if len(div) == 1:
                #'https://www.bcn.cl'
                url_item = 'https://www.bcn.cl'+div[0]['href']
                url.append(url_item)
                continue
            else:            
                for a in div:
                    # SERVEL incluye acentos hasta 2009
                    if eleccion <= 2009:
                        nombreBCN = a.contents[0].rsplit(' ',2)[0]
                    else:
                        nombreBCN = unidecode(a.contents[0].rsplit(' ',2)[0])                        
                    
                    if item[0] in nombreBCN:
                        url_item = 'https://www.bcn.cl'+a['href']
                        url.append(url_item)
                        break
            
        if i == 3 and not url_item :
            url.append([''])

    electos.loc[url_mask,'url'] = url