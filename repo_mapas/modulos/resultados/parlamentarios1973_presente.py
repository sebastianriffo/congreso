#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

def parlamentarios1973_presente(path_datos, candidatos, eleccion, rep):
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

    subdivrow = {0:'Distrito',1:'Circunscripción'}[rep]    
    pactos = pactos_electorales(eleccion)

    ## AGREGAR SENADORES AL LISTADO ORIGINAL DE CANDIDATOS
    if (rep == 1) and not sorted(path_datos.glob('*Circunscripcion*_candidatos.csv')):        
        path_datos_prev = path_datos.parents[0]/str(eleccion-4)
        datos_filenames = sorted(path_datos_prev.glob('*Circunscripcion*_electos.csv'))

        if datos_filenames:
            electos_prev = pd.read_csv(datos_filenames[0]) 
    
            if eleccion >= 2021:
                # electos_prev = electos_prev[electos_prev['Circunscripción'].isin([1,2,4,6,9,11,14] if (eleccion-2021)%8 == 0 else [3,5,7,8,10,12,13,15,16]) & (electos_prev['Electos_comp'] == '*')]
                electos_prev = electos_prev[electos_prev['Circunscripción'].isin(["Arica y Parinacota", "Tarapacá", "Atacama", "Valparaíso", "Maule", "Araucanía", "Aysén"])*((eleccion-2021)%8 == 0) & (electos_prev['Electos_comp'] == '*')]
            elif eleccion >= 1993: 
                # electos_prev = electos_prev[electos_prev['Circunscripción'].isin([2,4,7,8,9,12,13,16,17,19] if (eleccion-1993)%8 == 0 else [1,3,5,6,10,11,14,15,18]) & (electos_prev['Electos_comp'] == '*')]
                electos_prev = electos_prev[electos_prev['Circunscripción'].isin(["Tarapacá", "Atacama", "Valparaíso Cordillera", "Valparaíso Costa", "Maule Norte", "Maule Sur", "Araucanía Norte", "Araucanía Sur", "Aysén"])*((eleccion-1993)%8 != 0) & (electos_prev['Electos_comp'] == '*')]
            elif eleccion == 1973:
                # electos_prev = electos_prev[electos_prev['Circunscripción'].isin([1,3,5,7,9]) & (electos_prev['Electos_comp'] == '*')]
                electos_prev = electos_prev[electos_prev['Circunscripción'].isin(['Tarapacá y Antofagasta', 'Aconcagua y Valparaíso', "O'Higgins y Colchagua", 'Ñuble, Concepción y Arauco', 'Valdivia, Osorno y Llanquihue']) & (electos_prev['Electos_comp'] == '*')]
                electos_prev['Electos'] = '*'
                
            # cambios en militancia de un período a otro
            if eleccion == 2017:                
                #redistritaje
                electos_prev['Circunscripción'] = electos_prev['Circunscripción'].replace({"Santiago Oriente":"Santiago", "Bío-Bío Costa":"Bío-Bío", "Bío-Bío Cordillera":"Bío-Bío"})
                                
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
            elif eleccion == 2001: 
                electos_prev.loc[electos_prev['Partido'].str.contains("IND"), 'Partido'] = 'UDI'
            elif eleccion == 1993:
                print('holi')
                electos_prev.loc[electos_prev['Candidatos'].str.contains("Sule"), 'Partido'] = 'PR'
                electos_prev.loc[electos_prev['Candidatos'].str.contains("Cooper"),'Partido'] = 'RN'
                electos_prev.loc[electos_prev['Candidatos'].str.contains("Calderón"),'Partido'] = 'PS'
                electos_prev.loc[electos_prev['Candidatos'].str.contains("Piñera"),'Partido'] = 'RN'
                
            # ajustar pactos                
            prev_IND = {}        
            for partido in set(electos_prev[electos_prev['Partido'] != 'IND']['Partido']):
                if partido in pactos.keys():
                    prev_IND[electos_prev[electos_prev['Partido'] == partido]['Lista/Pacto'].values[0]] = pactos[partido]
                    electos_prev.loc[electos_prev['Partido'] == partido,'Lista/Pacto'] = pactos[partido]
            #problema : si un partido se sale de un pacto y hay IND
            electos_prev = electos_prev.replace({'Lista/Pacto':prev_IND}) 
                        
            electos_prev['Candidatos'] = electos_prev['Candidatos'].apply(lambda x : literal_eval(str(x))).apply(' '.join)
            electos_prev['Votos'] = 0   
            electos_prev['Porcentaje'] = 0
            electos_prev['Electos'] = '*'
            electos_prev['Electos_comp'] = '*'
                    
        # Vitalicios y designados : https://es.wikipedia.org/wiki/Anexo:Senadores_designados_de_Chile
        if 1989 <= eleccion < 2005: 
            if eleccion <= 1993:
                designados = [['SUPREMA','Ricardo Martín Díaz'],
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
            
            # circ 101: designados y vitalicios
            designados['Circunscripción'] = "Designados"         
            designados['Lista/Pacto']  = pactos['UDI']
        
            if eleccion == 1997 :
                designados.loc[[False]*6+[True]*4+[False],'Lista/Pacto'] = pactos['PDC']
        
            # designados = designados.set_index(['Circunscripción','Lista/Pacto','Partido'])        
            designados['Votos'] = 0
            designados['Porcentaje'] = 0
            designados['Electos'] = '*'
            designados['Electos_comp'] = '*'            
            designados['url'] = ''
            
            # concatenar
            if eleccion == 1989:
                candidatos = pd.concat([candidatos, designados], axis=0)  
            else:
                candidatos = pd.concat([candidatos, electos_prev, designados], axis=0)              
        else:
            candidatos = pd.concat([candidatos, electos_prev], axis=0)
    
    candidatos = candidatos[[subdivrow, 'Lista/Pacto', 'Partido', 'Candidatos', 'Votos', 'Porcentaje', 'Electos', 'Electos_comp', 'url']]
        
    ## AGREGAR REEMPLAZANTES AL DATAFRAME ELECTOS
    electos = candidatos[candidatos['Electos'] == '*'] 
    reemplazados = []

    if eleccion == 1989: 
        reemplazados = {0:['Vilicic Karnincic'], 1:['Guzmán Errázuriz', 'Eduardo Frei Ruiz-Tagle', 'Ruiz Danyau']}[rep]

        if (rep == 1) and not sum(electos['Candidatos'].str.contains('María Elena Carrera Villavicencio')): 
            electos.loc[max(electos.index)+1,:] = "Santiago Poniente", pactos['RN'], 'RN', 'Miguel Otero Lathrop', 0, 0,'','*',''            
            electos.loc[max(electos.index)+1,:] = "Santiago Oriente", pactos['PS'], 'PS', 'María Elena Carrera Villavicencio', 0, 0,'','*',''

    if eleccion == 2001: 
        reemplazados = {0:['^$'], 1:['Pinochet Ugarte']}[rep]        

    if eleccion == 2005:         
        reemplazados = {0:['Pérez Opazo'], 1:['Lavandero Illanes']}[rep]

        if (rep == 0) and not sum(electos['Candidatos'].str.contains('Néstor Jofré Núñez')): 
            electos.loc[max(electos.index)+1,:] = 'D2', pactos['RN'], 'RN', 'Néstor Jofré Núñez', 0, 0,'','*',''            

        if (rep == 1) and not sum(electos['Candidatos'].str.contains('Guillermo Vásquez Úbeda')): 
            electos.loc[max(electos.index)+1,:] = "Araucanía Sur", pactos['PRSD'], 'PRSD', 'Guillermo Vásquez Úbeda', 0, 0,'','*',''            
        
    if eleccion == 2009:
        reemplazados = {0:['García-Huidobro Sanfuentes'], 1:['Longueira Montes', 'Chadwick Piñera', 'Allamand Zavala', 'Matthei']}[rep] 

        if (rep == 0) and not sum(electos['Candidatos'].str.contains('Kort Garriga')):
            electos.loc[max(electos.index)+1,:] = 'D32', pactos['UDI'], 'UDI', 'Issa Kort Garriga', 0, 0,'','*',''
            
        if (rep == 1) and not sum(electos['Candidatos'].str.contains('von Baer Jahn')): 
            electos.loc[max(electos.index)+1,:] = "Santiago Oriente", pactos['UDI'], 'UDI', 'Ena von Baer Jahn', 0, 0,'','*',''
            electos.loc[max(electos.index)+1,:] = "O'Higgins", pactos['UDI'], 'UDI', 'Alejandro García-Huidobro Sanfuentes', 0, 0,'','*',''
            electos.loc[max(electos.index)+1,:] = "Los Ríos", pactos['RN'], 'RN', 'Carlos Larraín Peña', 0, 0,'','*',''
            electos.loc[max(electos.index)+1,:] = "Coquimbo", pactos['UDI'], 'UDI', 'Gonzalo Uriarte Herrera', 0, 0,'','*',''
            
    if eleccion == 2013: 
        #revisar
        reemplazados = {0:['Insunza De las Heras', 'Martínez Labbé'], 1:['Rincón González']}[rep]

        if (rep == 0) and not sum(electos['Candidatos'].str.contains('Miguel Ángel Alvarado Ramírez')): 
            electos.loc[max(electos.index)+1,:] = 'D9', pactos['PPD'], 'PPD', 'Miguel Ángel Alvarado Ramírez', 0, 0,'','*',''
        if (rep == 1) and not sum(electos['Candidatos'].str.contains('Manuel Matta Aragay')): 
            electos.loc[max(electos.index)+1,:] = "Maule Sur", pactos['PDC'], 'PDC', 'Manuel Matta Aragay', 0, 0,'','*',''

    if eleccion == 2017:
        reemplazados = {0:['Gutiérrez Gálvez', 'Melero Abaroa', 'Desbordes Jiménez', 'Sabat Fernández', 'Bellolio Avaria', 'Garín González', 'Kort Garriga', 'Carvajal Ambiado'], 
                        1:['Allamand Zavala', 'Harboe Bascuñán', 'Pérez Varela']}[rep]        

        if (rep == 0) and not sum(electos['Candidatos'].str.contains('Rubén Moraga Mamani')): 
            electos.loc[max(electos.index)+1,:] = 'D2', pactos['PC'], 'PC', 'Rubén Moraga Mamani', 0, 0,'','*',''
            electos.loc[max(electos.index)+1,:] = 'D8', pactos['UDI'], 'UDI', 'Cristián Labbé Martínez', 0, 0,'','*',''            
            electos.loc[max(electos.index)+1,:] = 'D8', pactos['RN'], 'RN', 'Camilo Morán Bahamondes', 0, 0,'','*',''
            electos.loc[max(electos.index)+1,:] = 'D10', pactos['RN'], 'RN', 'Tomás Fuentes Barros', 0, 0,'','*',''
            electos.loc[max(electos.index)+1,:] = 'D14', pactos['UDI'], 'UDI', 'Nora Cuevas Contreras', 0, 0,'','*',''
            electos.loc[max(electos.index)+1,:] = 'D14', pactos['RD'], 'RD', 'Marcela Sandoval Osorio', 0, 0,'','*',''            
            electos.loc[max(electos.index)+1,:] = 'D15', pactos['UDI'], 'UDI', 'Juan Manuel Masferrer Vidal', 0, 0,'','*',''
            electos.loc[max(electos.index)+1,:] = 'D19', pactos['PPD'], 'PPD', 'Patricia Rubio Escobar', 0, 0,'','*',''
            
        if (rep == 1) and not sum(electos['Candidatos'].str.contains('Marcela Sabat Fernández')): 
            electos.loc[max(electos.index)+1,:] = "Santiago", pactos['RN'], 'RN', 'Marcela Sabat Fernández', 0, 0,'','*',''
            electos.loc[max(electos.index)+1,:] = "Bío-Bío", pactos['PPD'], 'PPD', 'María Loreto Carvajal Ambiado', 0, 0,'','*',''        
            electos.loc[max(electos.index)+1,:] = "Bío-Bío", pactos['UDI'], 'UDI', 'Claudio Alvarado Andrade', 0, 0,'','*',''
            
    if eleccion == 2021: 
        reemplazados = {0:['^$'], 1:['Elizalde Soto']}[rep]        
        
        if (rep == 1) and not sum(electos['Candidatos'].str.contains('Vodanovic Rojas')): 
            electos.loc[max(electos.index)+1,:] = "Santiago", pactos['PS'], 'PS', 'Paulina Vodanovic Rojas', 0, 0,'','*',''        

    if reemplazados:               
        electos.loc[electos['Candidatos'].str.contains('|'.join(reemplazados)), 'Electos_comp'] = None
    
    return (candidatos, electos)
