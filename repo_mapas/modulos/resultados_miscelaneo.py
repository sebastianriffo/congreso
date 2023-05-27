"""
Pequeñas rutinas utilizadas por el módulo *resultados_elecciones*.

- nombres_formato : toma un nombre y lo separa en nombres y apellidos. Esto sirve, 
principalmente, para el diagrama de la nueva legislatura en mapa_parlamentario.
- biografiasBCN : url asociada a cada parlamentario electo, correspondiente a su 
biografía en la BCN, en el período 1989-presente.
"""

from unidecode import unidecode

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import time 
import pandas as pd
pd.options.mode.chained_assignment = None

#%%
def nombres_formato(candidatos, formato=True):
    """
    Toma la columna 'Candidatos' de un dataframe y separa cada nombre en una 
    una lista de sus nombres y apellidos.

    Parámetros
    ----------
    candidatos : dataframe
        Información de candidatos.
    formato : boolean, opcional
        Por defecto un nombre viene ordenado por nombres y apellidos. 
        'False' si ocurre lo contrario.

    Entrega
    -------
    nombres : dataframe
        Nombres de candidatos en el nuevo formato.

    """

    excepciones = {'Díaz De Valdés':'Díaz+de+Valdés',
                   'Diaz De Valdes':'Diaz+de+Valdes',
                   'García De la Huerta':'García+de+la+Huerta',
                   'García de la Huerta':'García+de+la+Huerta',                   
                   'Garcia de la Huerta':'García+de+la+Huerta',   
                   'Gregorio De Las Heras':'Gregorio+de+las+Heras',
                   'Ladrón de Guevara':'Ladrón+de+Guevara',
                   'Ladrón De Guevara':'Ladrón+de+Guevara',                   
                   'Lerdo De Tejada':'Lerdo+de+Tejada',
                   'Niño De Zepeda':'Niño+de+Zepeda',
                   'Niño de Zepeda':'Niño+de+Zepeda',
                   'Peña Y Lillo':'Peña+y+Lillo',
                   'Peña y Lillo':'Peña+y+Lillo',                   
                   'Pérez de Arce':'Pérez+de+Arce',
                   'Pérez De Arce':'Pérez+de+Arce',                   
                   'Ponce de León':'Ponce+de+León',
                   'Ruiz de Gamboa':'Ruíz+de+Gamboa',
                   'Ruiz De Gamboa':'Ruíz+de+Gamboa',
                   'Solo De Zaldívar':'Solo+de+Zaldívar',
                   'Solo De Zaldivar':'Solo+de+Zaldivar',
                   #
                   'Cruz Coke':'Cruz-Coke',
                   'Garcia Huidobro':'García-Huidobro',
                   'García Huidobro':'García-Huidobro',                   
                   'Jocelyn Holt':'Jocelyn-Holt',
                   'Larraín García Moreno': 'Larraín García-Moreno',
                   # 'Mac-Clure': 'Mac+Clure',
                   'Pérez Cotapos':'Pérez-Cotapos',
                   'Viale Rigo':'Viale-Rigo',
                   'Viera Gallo':'Viera-Gallo',
                   'Rigo Righi':'Rigo-Righi',
                   'Ruiz Tagle':'Ruiz-Tagle',
                   'Ruiz Esquide':'Ruiz-Esquide',
                   #
                   'Dalbora': "D'Albora",
                   'O Ryan': "O'Ryan",
                   #                                      
                   'Yrarrázaval': 'Irarrázaval',
                   #
                   'Brucher': 'Brücher',
                   'Buchi': 'Büchi',
                   'Doll': 'Döll',
                   'Hubner': 'Hübner',
                   'Muhlenbrock': 'Mühlenbrock',
                   'Muller': 'Müller'}
    
    articulos = {' Y ':' Y+',
                 ' De La ':' de+la+', ' De Los ':' de+los+', ' De Las ':' de+las+', ' De ':' de+', ' Del ':' del+', ' del ':' del+', 
                 ' San ':' San+', ' Santa ':' Santa+', 
                 ' Van ':' van+', ' Von ':' von+', '-Von ':'-von+', 
                 ' Mac ':' Mac+',
                 ' La ':' La+', ' Le ':' Le+',
                 ' Da ':' Da+'}
    
    nombres = candidatos[['Candidatos']].copy()
            
    nombres['Candidatos'] = nombres['Candidatos'].replace({'^Raúl Armando Barrionuevo$' : 'Raúl Armando Barrionuevo Barrionuevo', #1973
                                                           '^Anselmo del Rosario Quezada$' : 'Anselmo del Rosario Quezada Quezada',
                                                           '^Alejandro Bell Jara$' : 'Alejandro Bell Jaras'}, 
                                                            regex=True)   
        
    # errores en SERVEL (al 16/01/2023)
    nombres['Candidatos'] = nombres['Candidatos'].replace({'Venturafaulbaum' : 'Ventura Faulbaum',          #1989, D58
                                                           'álvarez-Salamán' : 'Alvarez-Salamanca',         #1989-97, D38
                                                           'van Rysselbergh Varela' : 'van Rysselberghe Varela', #1997, D44
                                                           'Manouchehr Manouchehri Moghadam Kashan Lobos' : 'Daniel Manouchehri Lobos', #2009, D8
                                                           'DE LAS HERAS DE LAS HERAS' : 'DE LAS HERAS',    #2013, D9
                                                           'KASHAN LOBOS MANOUCHEHRI MOGHADAM' : 'Manouchehri Lobos Daniel' #2021, D5 
                                                           },
                                                           regex=True)   
    
    nombres['Candidatos'] = nombres['Candidatos'].str.title().replace(excepciones, regex=True).replace(articulos, regex=True).str.split()   
        
    if not formato:
        # se asume que tienen dos apellidos
        nombres['Candidatos'] = nombres['Candidatos'].map(lambda x: x[2:] +x[0:2] if len(x) > 2 else (x[1]+x[0] if len(x) > 0 else x))
        
    nombres['Candidatos'] = nombres['Candidatos'].map(lambda x: tuple([u.replace('+',' ') for u in x]))
    
    return nombres

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
                ((electos.index.get_level_values(0) < 100) if subdivrow in electos.index.names else (electos[subdivrow] < 100))

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
