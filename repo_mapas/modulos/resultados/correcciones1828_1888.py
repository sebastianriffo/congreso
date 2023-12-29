#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 16:34:48 2023

@author: sebastian
"""

def correcciones1828_1888(candidatos, eleccion, rep):
    subdivrow = {0:'Distrito',1:'Circunscripción'}[rep]    
    
    candidatos.loc[candidatos['Partido'] == 'Independiente', 'Partido'] = 'Candidatura Independiente'

    reemplazados = {0:['^$'], 1:['^$']}[rep]
    reemplazantes = {0:['^$'], 1:['^$']}[rep]
    presuntivos = {0:['^$'], 1:['^$']}[rep]
    partidos = {'^$': {0:['^$'], 1:['^$']}[rep]}    
    
    """
    En este período hay
    - propietarios que escogieron el Senado (eliminados), 
    - propietarios fallecidos antes de asumir o que simplemente no asumieron (eliminados)
    - propietarios que escogen otra provincia (corregidos),
    - suplentes que asumen como propietarios, o propietarios registrados como suplentes en bcn (corregidos)
    - suplentes por más de una provincia (corregido: se repiten)    
    - elecciones presuntivas: 1864 (Petorca), 1870 (Cauquenes), 1882 (Llanquihue). Los propietarios presuntivos que se incorporaron por otra provincia no fueron repetidos.

    - revisar: elecciones complementarias
    - revisar: senado
    """
    propietarios = {0:['^$'], 1:['^$']}[rep]
    
    if eleccion == 1888:
        reemplazados = {0:['^$'],  
                        1:['Manuel Joaquín Valenzuela Castillo', 'Ramón Francisco Rozas Mendiburú', 'José Ignacio Vergara Urzúa', 'Jorge Segundo Huneeus Zegers', 'Miguel Elizalde Jiménez', 'Manuel García de la Huerta Pérez', 'Joaquín Valledor Pinto', 'Domingo Santa María González', 'Aniceto Vergara Albano', 'Javier Luis Zañartu Larraín']}[rep]

        if (rep == 0):
            candidatos.loc[candidatos['Candidatos'] == 'Arturo Maximiano Edwards Ross', ['Distrito', 'Electos']] = ['Cachapoal', '*']

            if not sum(candidatos['Candidatos'].str.contains('José Antonio Valdés González')):
                candidatos.loc[len(candidatos.index),:] = 'La Serena','','José Antonio Valdés González','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Antonio_Valdés_González'
                #
                candidatos.loc[len(candidatos.index),:] = 'Combarbalá','','Fernando Cabrera Gacitúa','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Fernando_Cabrera_Gacitúa'
                candidatos.loc[len(candidatos.index),:] = 'Rancagua','','Francisco Herboso España','Partido Liberal','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Francisco_Herboso_España'
        else:
            if not sum(candidatos['Candidatos'].str.contains('Manuel Joaquín Valenzuela Castillo')):
                candidatos.loc[len(candidatos.index),:] = 'Santiago','','José Clemente Cecilio Fabres Fernández de Leiva','Partido Conservador','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Clemente_Cecilio_Fabres_Fernández_de_Leiva'
                candidatos.loc[len(candidatos.index),:] = 'Curicó','','Manuel Joaquín Valenzuela Castillo','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Manuel_Joaquín_Valenzuela_Castillo'

            candidatos = candidatos[~candidatos['Candidatos'].isin(['José Manuel Balmaceda Fernández',
                                                                    'José Eugenio Vergara Galeas', 'Marcial González Ibieta', 'Manuel Beauchef Manso de Velasco', 'Manuel Beauchef Manso Velasco'
                                                                    ])]

    if eleccion == 1885:
        propietarios = {0:['Nicolás R. Peña Vicuña', 'Liborio Sánchez Cárdenas'], 1:['^$']}[rep]
        reemplazados = {0:['^$'],  
                        1:['Antonio Varas de la Barra', 'José Joaquín Laso Castillo', 'José Manuel Balmaceda Fernández', 'José Eugenio Vergara Galeas', 'Carlos Antúnez González', 'Marcial González Ibieta']}[rep]
        if (rep == 0):
            candidatos.loc[candidatos['Candidatos'] == 'Vicente Dávila Larraín', ['Distrito', 'Electos']] = ['Concepción', '*']
            candidatos.loc[candidatos['Candidatos'] == 'Luis Martiniano Rodríguez Herrera', ['Distrito', 'Electos']] = ['Quinchao', '*']

            if not sum(candidatos['Candidatos'].str.contains('José Antonio Valdés González')):
                candidatos.loc[len(candidatos.index),:] = 'Combarbalá','','José Antonio Valdés González','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Antonio_Valdés_González'
                #
                candidatos.loc[len(candidatos.index),:] = 'San Felipe','','Jacinto Chacón Barrios','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Jacinto_Chacón_Barrios'
                candidatos.loc[len(candidatos.index),:] = 'Cachapoal','','Francisco Herboso España','Partido Liberal','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Francisco_Herboso_España'
        else:
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Ramón Allende Padín', 'Jovino Novoa Vidal', #fallecidos
                                                                    'Pedro Vicente Reyes Palazuelos', 'Carlos de la Cruz Valdés Izquierdo',                                                                    
                                                                    'Francisco Freire Caldera'
                                                                    ])]
            
            if not sum(candidatos['Candidatos'].str.contains('Manuel Joaquín Valenzuela Castillo')):
                candidatos.loc[len(candidatos.index),:] = 'Santiago','','José Clemente Cecilio Fabres Fernández de Leiva','Partido Conservador','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Clemente_Cecilio_Fabres_Fernández_de_Leiva'
                candidatos.loc[len(candidatos.index),:] = 'Curicó','','Manuel Joaquín Valenzuela Castillo','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Manuel_Joaquín_Valenzuela_Castillo'
                #
                candidatos.loc[len(candidatos.index),:] = 'Valdivia','','Vicente Izquierdo Urmeneta','','','','','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Vicente_Izquierdo_Urmeneta'
        
    if eleccion == 1882:        
        propietarios = {0:['José Agustín Tagle Montt'], 1:['^$']}[rep]
        reemplazados = {0:['^$'],  
                        1:['Liborio Ramón Freire Caldera', 'José Eugenio Vergara Galeas', 'Jovino Novoa Vidal']}[rep]       
        reemplazantes = {0:['^$'], 
                         1:['Adolfo Valderrama Sainz de la Peña']}[rep]
        presuntivos = {0:['Victorino Rojas Magallanes', 'Nicolás Naranjo Palacios', 'Juan Francisco Mujica Valenzuela', ], 
                       1:['^$']}[rep]

        if (rep == 0): 
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Patricio Javier Lynch Zaldívar', 'Francisco Valdés Vergara'])] #no se incorporaron
        
            if not sum(candidatos['Candidatos'].str.contains('Alejandro Fierro Pérez de Camino')):
                candidatos.loc[len(candidatos.index),:] = 'Santiago','','Alejandro Fierro Pérez de Camino','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Alejandro_Fierro_Pérez_de_Camino'
        else:
            candidatos = candidatos[~candidatos['Candidatos'].isin(['José Victorino Lastarria Santander', 'Marcial Martínez Cuadros',  #mision diplomatica
                                                                    'Domingo Santa María González',
                                                                    'Rafael Sotomayor Baeza', 
                                                                    'Arístides Martínez Cuadros', 'Joaquín Valledor Pinto',
                                                                    ])] 
            
            candidatos.loc[candidatos['Candidatos'].isin(['Benjamín Vicuña Mackenna']), 'Circunscripción'] = 'Coquimbo'
            candidatos.loc[candidatos['Candidatos'].isin(['Adolfo Valderrama Sainz de la Peña']), 'Circunscripción'] = 'Ñuble'

            if not sum(candidatos['Candidatos'].str.contains('Domingo Atanasio Fernández Concha')):
                candidatos.loc[len(candidatos.index),:] = 'Santiago','','Domingo Atanasio Fernández Concha','Partido Conservador','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Domingo_Atanasio_Fernández_Concha'
                candidatos.loc[len(candidatos.index),:] = 'Curicó','','Manuel Joaquín Valenzuela Castillo','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Manuel_Joaquín_Valenzuela_Castillo'
                candidatos.loc[len(candidatos.index),:] = 'Chiloé','','José Joaquín Laso Castillo','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Joaquín_Laso_Castillo'
                #
                candidatos.loc[len(candidatos.index),:] = 'Valdivia','','Vicente Izquierdo Urmeneta','','','','','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Vicente_Izquierdo_Urmeneta'

    if eleccion == 1879:
        # DIPUTADOS
        # Francisco Carvallo Elizalde, suplente por Combarbalá y Cañete
        # José Antonio Soffia, suplente por Petorca y Osorno
        
        propietarios = {0:['Agustín Segundo Rodríguez Azócar', 'Ramón Ricardo Rozas Garfias'], 
                        1:['^$']}[rep]
        reemplazados = {0:['^$'], 
                        1:['Manuel Jerónimo Urmeneta García', 'Manuel Montt Torres', 'Domingo Santa María González', 'Rafael Sotomayor Baeza', 'José Victorino Lastarria Santander']}[rep]  

        if (rep == 0):
            candidatos.loc[candidatos['Candidatos'] == 'Aniceto Vergara Albano', ['Distrito', 'Electos']] = ['Chillán', '*'] #en «Anales» aparece como propietario en dos provincias: los andes y chillán (bcn considera esta)
            candidatos.loc[candidatos['Candidatos'] == 'José Francisco Vergara Donoso', ['Distrito', 'Electos']] = ['Quinchao', '*']
        
            candidatos.loc[candidatos['Candidatos'] == 'Justo García', ['Electos']] = [None]        

            if not sum(candidatos['Candidatos'].str.contains('José Clemente Cecilio Fabres')):
                candidatos.loc[len(candidatos.index),:] = 'Santiago','','José Clemente Cecilio Fabres Fernández de Leiva','Partido Conservador','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Clemente_Cecilio_Fabres_Fernández_de_Leiva'
                candidatos.loc[len(candidatos.index),:] = 'Caupolicán','','Raimundo Larraín Covarrubias','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Raimundo_Larraín_Covarrubias'
                candidatos.loc[len(candidatos.index),:] = 'Itata','','Alejandro Fierro Pérez de Camino','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Alejandro_Fierro_Pérez_de_Camino'
                #
                candidatos.loc[len(candidatos.index),:] = 'Melipilla','','Gaspar Toro Hurtado','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Gaspar_Toro_Hurtado'
                candidatos.loc[len(candidatos.index),:] = 'Cañete','','Francisco Carvallo Elizalde','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Francisco_Carvallo_Elizalde'            
                candidatos.loc[len(candidatos.index),:] = 'Osorno','','José Antonio Soffia Argomedo','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Antonio_Soffia_Argomedo'            
        else:
            candidatos.loc[candidatos['Candidatos'].isin(['José Rafael Larraín Moxó']), 'Circunscripción'] = 'Santiago'
            candidatos.loc[candidatos['Candidatos'].isin(['Manuel José Irarrázaval Larraín']), 'Circunscripción'] = 'Santiago'
            candidatos.loc[candidatos['Candidatos'].isin(['Ramón Francisco Rozas Mendiburú']), 'Circunscripción'] = 'Linares' 
            candidatos.loc[candidatos['Candidatos'].isin(['José Luis Donoso Cienfuegos']), 'Circunscripción'] = 'Linares' 

            candidatos = candidatos[~candidatos['Circunscripción'].isin(['Nacional-1'])]
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Pedro León Gallo Goyenechea', 'Pedro Eulogio Altamirano Aracena', 'Diego Antonio Tagle Echeverría',
                                                                    'Adolfo Eastman Quiroga', 'Ricardo Claro Cruz', 
                                                                    'Santiago Lindsay Font', 'Diego Vergara Albano'])] #suplentes fallecidos
            
            candidatos.loc[candidatos['Candidatos'].isin(['Benjamín Vicuña Mackenna']), 'Circunscripción'] = 'Coquimbo'
                
            if not sum(candidatos['Candidatos'].str.contains('Álvaro José Miguel Covarrubias Ortúzar')):
                candidatos.loc[len(candidatos.index),:] = 'Santiago','','Domingo Atanasio Fernández Concha','Partido Conservador','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Domingo_Atanasio_Fernández_Concha'
                candidatos.loc[len(candidatos.index),:] = 'Santiago','','Álvaro José Miguel Covarrubias Ortúzar','Partido Liberal','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Álvaro_José_Miguel_Covarrubias_Ortúzar'
                candidatos.loc[len(candidatos.index),:] = 'Curicó','','Alejandro Matías Luis Ignacio Reyes Cotapos','Partido Liberal','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Alejandro_Matías_Luis_Ignacio_Reyes_Cotapos'
                candidatos.loc[len(candidatos.index),:] = 'Curicó','','Manuel Joaquín Valenzuela Castillo','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Manuel_Joaquín_Valenzuela_Castillo'
                candidatos.loc[len(candidatos.index),:] = 'Linares','','José Luis Donoso Cienfuegos','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Luis_Donoso_Cienfuegos'
                candidatos.loc[len(candidatos.index),:] = 'Arauco','','Maximiano Errázuriz Valdivieso','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Maximiano_Errázuriz_Valdivieso'
                candidatos.loc[len(candidatos.index),:] = 'Chiloé','','Manuel Montt Torres','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Manuel_Montt_Torres'
                #
                candidatos.loc[len(candidatos.index),:] = 'Chiloé','','José Tomás Besa Infantas','Partido Nacional o Monttvarista','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Tomás_Besa_Infantas'
    
    if eleccion == 1876:
        # DIPUTADOS
        # Rafael García-Huidobro, suplente por Mulchén y Lebu
        # SENADORES
        # la cámara se renovó por completo para tener representación provincial
                
        propietarios = {0:['José Ramón Yávar Jiménez', 'Julio Lecaros Valdés', 'Adolfo Carrasco Albano', 'Juan Eduardo Mackenna Astorga'], 
                        1:['José Luis Donoso Cienfuegos']}[rep]
        reemplazados = {0:['^$'], 
                        1:['José Luis Borgoño Vergara', 'Juan de Dios Correa de Saa Martínez', 'Pedro León Gallo Goyenechea', 'Agustín Edwards Ossandón', 'Pedro Eulogio Altamirano Aracena', 'Diego Antonio Tagle Echeverría']}[rep]

        if (rep == 0):
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Benjamín Vicuña Mackenna', 'Manuel Jerónimo Urmeneta García'])] #escogieron el senado 

            candidatos.loc[candidatos['Candidatos'] == 'Enrique Cood Ross', ['Distrito', 'Electos']] = ['Melipilla', '*']
                
            if not sum(candidatos['Candidatos'].str.contains('Francisco Prado Aldunate')):
                candidatos.loc[len(candidatos.index),:] = 'Santiago','','Francisco Prado Aldunate','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Francisco_Prado_Aldunate'
                candidatos.loc[len(candidatos.index),:] = 'Santiago','','José Clemente Cecilio Fabres Fernández de Leiva','Partido Conservador','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Clemente_Cecilio_Fabres_Fernández_de_Leiva'
                #
                candidatos.loc[len(candidatos.index),:] = 'Lautaro','','Luis Montt Montt','Partido Nacional','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Luis_Montt_Montt'
                candidatos.loc[len(candidatos.index),:] = 'Lebu','','Rafael García-Huidobro Luco','Partido Nacional','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Rafael_García_Huidobro_Luco'
        else:
            candidatos.loc[candidatos['Candidatos'].isin(['José Rafael Larraín Moxó']), 'Circunscripción'] = 'Santiago'
            candidatos.loc[candidatos['Candidatos'].isin(['Manuel José Irarrázaval Larraín']), 'Circunscripción'] = 'Santiago'
            candidatos.loc[candidatos['Candidatos'].isin(['Juan de Dios Correa de Saa Martínez']), 'Circunscripción'] = 'Santiago'
            candidatos.loc[candidatos['Candidatos'].isin(['Ramón Francisco Rozas Mendiburú']), 'Circunscripción'] = 'Ñuble' 
            candidatos.loc[candidatos['Candidatos'].isin(['José Luis Donoso Cienfuegos']), 'Circunscripción'] = 'Linares' 

            candidatos = candidatos[~candidatos['Circunscripción'].isin(['Nacional-1'])]
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Francisco Massenlli Guarda', 'Santiago Lindsay Font', 'Miguel Luis Amunátegui Aldunate',
                                                                    'Manuel Antonio Matta Goyenechea', 'José María Barceló Carvallo', 'Manuel Martín José Recabarren Rencoret',
                                                                    'Marcial González Ibieta'])]
            
            candidatos.loc[candidatos['Candidatos'] == 'Antonio Varas de la Barra', 'Circunscripción'] = 'Talca'
            candidatos.loc[candidatos['Candidatos'] == 'Pedro Nolasco Marcoleta Dávila', 'Circunscripción'] = 'Bío-Bío'            
                        
            if not sum(candidatos['Candidatos'].str.contains('Álvaro José Miguel Covarrubias Ortúzar')):
                candidatos.loc[len(candidatos.index),:] = 'Valparaíso','','Agustín Edwards Ossandón','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Agustín_Edwards_Ossandón'
                candidatos.loc[len(candidatos.index),:] = 'Santiago','','Álvaro José Miguel Covarrubias Ortúzar','Partido Liberal','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Álvaro_José_Miguel_Covarrubias_Ortúzar'
                candidatos.loc[len(candidatos.index),:] = 'Curicó','','Manuel Joaquín Valenzuela Castillo','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Manuel_Joaquín_Valenzuela_Castillo'
                candidatos.loc[len(candidatos.index),:] = 'Curicó','','Alejandro Matías Luis Ignacio Reyes Cotapos','Partido Liberal','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Alejandro_Matías_Luis_Ignacio_Reyes_Cotapos'
                candidatos.loc[len(candidatos.index),:] = 'Chiloé','','Manuel Montt Torres','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Manuel_Montt_Torres'
                candidatos.loc[len(candidatos.index),:] = 'Chiloé','','José Tomás Besa Infantas','Partido Nacional o Monttvarista','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Tomás_Besa_Infantas'
                candidatos.loc[len(candidatos.index),:] = 'Arauco','','Antonio del Pedregal Velasco','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Antonio_Del_Pedregal_Velasco'
                
    if eleccion == 1873:
        propietarios = {0:['Ricardo Lecaros Vicuña', 'Fernando Liborio Lazcano Echaurren', 'Juan Esteban Rodríguez Segura'], 
                        1:['Miguel Barros Morán']}[rep]

        if (rep == 0):
            candidatos.loc[candidatos['Candidatos'] == 'Pedro Eulogio Altamirano Aracena', ['Distrito', 'Electos']] = ['Concepción', '*']
        
            if not sum(candidatos['Candidatos'].str.contains('José Clemente Cecilio Fabres')):
                candidatos.loc[len(candidatos.index),:] = 'Rancagua','','José Clemente Cecilio Fabres Fernández de Leiva','Partido Conservador','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Clemente_Cecilio_Fabres_Fernández_de_Leiva'
                #
                candidatos.loc[len(candidatos.index),:] = 'Laja','','Marcos Orrego Garmendía','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Marcos_Orrego_Garmendia'
        else:
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Federico Errázuriz Zañartu',
                                                                    'Manuel Alcalde Velasco', 'Juan José Aldunate Irarrázaval', 'Manuel Antonio Tocornal Grez'])]
                                                                    
            candidatos.loc[candidatos['Candidatos'].isin(['Miguel Barros Morán']), 'Circunscripción'] = 'Nacional-3'
            #
            # corregir nombre
            candidatos.loc[candidatos['Candidatos'].isin(['Manuel Beauchef Manso Velasco']), 'Candidatos'] = 'Manuel Beauchef Manso de Velasco'
            candidatos.loc[candidatos['Candidatos'].isin(['Manuel Beauchef Manso de Velasco']), 'Circunscripción'] = 'Nacional-2'
    
    if eleccion == 1870:        
        propietarios = {0:['Juan José Cerda', 'Pedro Nolasco Videla Hidalgo', 'Miguel Cruchaga Montt', 'Isidoro Errázuriz Errázuriz', 'Luis Martiniano Rodríguez Herrera', 'Rafael Wormald Ramírez'], 
                        1:['Francisco de Borja García-Huidobro Aldunate', 'Marcos Maturana del Campo', 'Miguel Barros Morán', 
                           'Pedro Félix Vicuña Aguirre']}[rep]
        presuntivos = {0:['Ruperto Ovalle Vicuña', 'Pablo Flores', 'José Antonio Soffia Argomedo', 'Miguel Castillo Andueza', #'Marcial Martínez Cuadros', 
                          'Pedro Lucio Cuadra Luque', 'Jovino Novoa Vidal', 'Blas Encinas', 'Manuel Salustio Fernández Pradel', #'Guillermo Matta Goyenechea', 
                          'Ricardo Claro Cruz', 'Evaristo del Campo Madariaga'], 1:['^$']}[rep]

        if (rep == 0):
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Aníbal Pinto Garmendía'])] #aceptó la senaduría
    
            candidatos.loc[candidatos['Candidatos'] == 'Abraham König Velásquez', ['Electos']] = [None]
            
            candidatos.loc[candidatos['Candidatos'] == 'Manuel Jerónimo Urmeneta García', ['Distrito', 'Electos']] = ['Quillota', '*']
            candidatos.loc[candidatos['Candidatos'] == 'Francisco de Paula Echaurren García-Huidobro', ['Distrito', 'Electos']] = ['Limache', '*']
            candidatos.loc[candidatos['Candidatos'] == 'Marcial Martínez Cuadros', ['Distrito', 'Electos']] = ['Cauquenes', '*']
            candidatos.loc[candidatos['Candidatos'] == 'José Eugenio Vergara Galeas', ['Distrito', 'Electos']] = ['Cauquenes', '*']
            candidatos.loc[candidatos['Candidatos'] == 'Francisco Segundo Puelma Castillo', ['Distrito', 'Electos']] = ['San Carlos', '*']
            candidatos.loc[candidatos['Candidatos'] == 'José Joaquín Blest Gana', ['Distrito', 'Electos']] = ['Chillán', '*']
            candidatos.loc[candidatos['Candidatos'] == 'Camilo Enrique Cobo Gutiérrez', ['Distrito', 'Electos']] = ['Chillán', '*']
            candidatos.loc[candidatos['Candidatos'] == 'Guillermo Matta Goyenechea', ['Distrito', 'Electos']] = ['Ancud', '*']
            
            candidatos.loc[candidatos['Candidatos'] == 'Enrique del Solar Marín', ['Distrito', 'Electos_comp']] = ['Curicó', '*']
    
            if not sum(candidatos['Candidatos'].str.contains('Francisco de Paula Echaurren González')):
                #existe una confusion entre ambos francisco de paula echaurren
                candidatos.loc[len(candidatos.index),:] = 'Combarbalá','','Francisco de Paula Echaurren González','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Francisco_de_Paula_Echaurren_González'
                #
                candidatos.loc[len(candidatos.index),:] = 'Quillota','','Emilio Crisólogo Varas Fernández','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Emilio_Crisólogo_Varas_Fernández'
        else:
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Manuel Carvallo Gómez', 'Bernardo del Solar Marín',
                                                                    'Santiago Segundo Pérez Larraín', 'Miguel María Guemes Fernández', 'Eugenio Domingo Torres Velasco',
                                                                    'Manuel Antonio Tocornal Grez', 'Manuel Alcalde Velasco',
                                                                    'Francisco Ignacio Ossa Mercado', 'Manuel Bulnes Prieto',
                                                                    'Juan José Aldunate Irarrázabal'])] 
           
            candidatos.loc[candidatos['Candidatos'].isin(['Pedro Félix Vicuña Aguirre', 'Juan José Aldunate Irarrázaval']), 'Circunscripción'] = 'Nacional-2'
            candidatos.loc[candidatos['Candidatos'].isin(['Francisco de Borja García-Huidobro Aldunate', 'Marcos Maturana del Campo', 'Miguel Barros Morán', 'Apolinario Soto Cuadros', 'Bernardino Bravo Aldunate']), 'Circunscripción'] = 'Nacional-3'                        
            
            if not sum(candidatos['Candidatos'].str.contains('Francisco Antonio Vargas Fontecilla')):
                candidatos.loc[len(candidatos.index),:] = 'Nacional-1','','Francisco Antonio Vargas Fontecilla','Partido Liberal','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Francisco_Antonio_Vargas_Fontecilla'
                candidatos.loc[len(candidatos.index),:] = 'Nacional-1','','Alejandro Matías Luis Ignacio Reyes Cotapos','Partido Liberal','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Alejandro_Matías_Luis_Ignacio_Reyes_Cotapos'
                candidatos.loc[len(candidatos.index),:] = 'Nacional-2','','Juan José Aldunate Irarrázaval','Partido Conservador','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_José_Aldunate_Irarrázabal'
            
    if eleccion == 1867:
        # DIPUTADOS
        # Santiago Guzmán, suplente por Putaendo y Nacimiento (fuente: Urzua-Valenzuela, pp.202-203)
        # Cirilo Vigil Avaria, suplente por Lautaro y Arauco
        # Francisco de Paula Pérez Caldera, suplente por San Felipe y Valdivia
        
        propietarios = {0:['Nicomedes Ossa Cerda', 'José Manuel Pinto Arias', 'Ramón Covarrubias Ortúzar', 'Manuel Amunátegui Aldunate'], 
                        1:['Marcos Maturana del Campo']}[rep]
        presuntivos = {0:['Isidoro Errázuriz Errázuriz', 'Jovino Novoa Vidal', 'Guillermo Matta Goyenechea'], 1:['^$']}[rep]
       
        if (rep == 0):
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Pedro Ugarte Ramírez', 'Federico Puga Borne'])] #falleció antes de iniciarse el período
                    
            candidatos.loc[candidatos['Candidatos'] == 'Eduardo Montes Solar', ['Electos']] = [None]
            candidatos.loc[candidatos['Candidatos'] == 'Juan de la Cruz Guzmán Guzmán', ['Electos']] = [None]
            candidatos.loc[candidatos['Candidatos'] == 'Ramón Valdés Lecaros', ['Electos']] = [None]
            
            if not sum(candidatos['Candidatos'].str.contains('Juan José Agustín Ugarte Guzmán')):
                candidatos.loc[len(candidatos.index),:] = 'San Fernando','','Juan José Agustín Ugarte Guzmán','Partido Conservador','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_José_Agustín_Ugarte_Guzmán'
                candidatos.loc[len(candidatos.index),:] = 'Constitución','','Juan de Dios Cisternas Moraga','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_de_Dios_Cisternas_Moraga'
                #
                candidatos.loc[len(candidatos.index),:] = 'La Serena','','Benjamín Vicuña Solar','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Benjamín_Vicuña_Solar' #fuente: Urzúa-Valenzuela, p.202
                candidatos.loc[len(candidatos.index),:] = 'Putaendo','','Santiago Guzmán','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Santiago_Guzmán'
                candidatos.loc[len(candidatos.index),:] = 'Quillota','','Ruperto Ovalle Vicuña','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Ruperto_Ovalle_Vicuña'
                candidatos.loc[len(candidatos.index),:] = 'Valparaíso','','Manuel José Higinio Vicuña Prado','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Manuel_José_Higinio_Vicuña_Prado'
                candidatos.loc[len(candidatos.index),:] = 'San Carlos','','Francisco Javier Reyes Cotapos','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Francisco_Javier_Reyes_Cotapos'
                candidatos.loc[len(candidatos.index),:] = 'Constitución','','Antonio Subercaseaux Vicuña','Partido Conservador','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Antonio_Subercaseaux_Vicuña'
                candidatos.loc[len(candidatos.index),:] = 'Lautaro','','Cirilo Vigil Avaria','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Cirilo_Vigil_Avaria', #fuente: Urzúa-Valenzuela, p.207
                candidatos.loc[len(candidatos.index),:] = 'Valdivia','','Francisco de Paula Pérez Caldera','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Francisco_de_Paula_Pérez_Caldera',            
                candidatos.loc[len(candidatos.index),:] = 'Castro','','Pablo Flores','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Pablo_Flores'
        else:
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Francisco Ignacio Ossa Mercado', 'Manuel Bulnes Prieto',
                                                                    'Apolinario Soto Cuadros', 'Bernardino Bravo Aldunate', 'Miguel Barros Morán', 'Pedro Félix Vicuña Aguirre'])]

            candidatos.loc[candidatos['Candidatos'].isin(['Domingo Matte Messía']), 'Circunscripción'] = 'Nacional-2'
            candidatos.loc[candidatos['Candidatos'].isin(['Marcos Maturana del Campo']), 'Circunscripción'] = 'Nacional-3'
            
            if not sum(candidatos['Candidatos'].str.contains('Álvaro José Miguel Covarrubias Ortúzar')):
                candidatos.loc[len(candidatos.index),:] = 'Nacional-1','','Álvaro José Miguel Covarrubias Ortúzar','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Álvaro_José_Miguel_Covarrubias_Ortúzar'
            
    if eleccion == 1864:
        # DIPUTADOS
        # José Joaquín Blest Gana, suplente por Santiago y Chillán
        # Carlos Castellón, suplente por Concepción y Coelemu
        # SENADORES
        # José Santiago Aldunate no aparece electo como subrogante de José Francisco Gana
                
        propietarios = {0:['Mariano José Ariztía Urmeneta', 'Vicente Izquierdo Urmeneta', 'Adriano Borgoño Vergara', 'Melchor Concha Toro', 'José Francisco Echenique Tagle', 'Miguel Cruchaga Montt', 'Diego Antonio Tagle Echeverría', 'Enrique Cood Ross'], 
                        1:['Manuel Alcalde Velasco', 'Eugenio Domingo Torres Velasco']}[rep]
        reemplazantes = {0:['^$'], 1:['Francisco Marín Recabarren']}[rep]
        presuntivos = {0:['Waldo Silva Algue', 'José Antonio García'], 1:['^$']}[rep] #el segundo es suplente presuntivo

        if (rep == 0):
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Manuel Camilo Vial Formas'])] #va por el senado
            
            candidatos.loc[candidatos['Candidatos'] == 'Antonio Varas de la Barra', ['Distrito', 'Electos']] = ['Santiago', '*']
            candidatos.loc[candidatos['Candidatos'] == 'Federico Errázuriz Zañartu', ['Distrito', 'Electos']] = ['Caupolicán', '*']
            
            if not sum(candidatos['Candidatos'].str.contains('Manuel Montt Torres')):
                candidatos.loc[len(candidatos.index),:] = 'Los Andes','','Manuel Montt Torres','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Manuel_Montt_Torres'
                #
                candidatos.loc[len(candidatos.index),:] = 'Chiilán','','José Joaquín Blest Gana','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Joaquín_Blest_Gana'
                candidatos.loc[len(candidatos.index),:] = 'Coelemu','','Carlos Castellón Larenas','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Carlos_Castellón_Larenas'
        else:
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Pedro García de la Huerta Saravia', 'Juan Agustín Alcalde Bascuñán', 
                                                                    'Diego Arriarán del Río',
                                                                    'Santiago Salas Palazuelos', 'Apolinario Soto Cuadros', 'Bernardino Bravo Aldunate', 'Marcos Maturana del Campo', 'Miguel Barros Morán',
                                                                    'José Santiago Aldunate Toro'])]  

            candidatos.loc[candidatos['Candidatos'].isin(['Eugenio Domingo Torres Velasco']), 'Circunscripción'] = 'Nacional-1'        
            candidatos.loc[candidatos['Candidatos'].isin(['Manuel Alcalde Velasco']), 'Circunscripción'] = 'Nacional-3' 
            #
            candidatos.loc[candidatos['Candidatos'].isin(['Patricio Larraín Gandarillas']), 'Circunscripción'] = 'Nacional-2'

            if not sum(candidatos['Candidatos'].str.contains('Santiago Segundo Pérez Larraín')):
                candidatos.loc[len(candidatos.index),:] = 'Nacional-1','','Santiago Segundo Pérez Larraín','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Santiago_Segundo_Pérez_Larraín'

        
    if eleccion == 1861:
        propietarios = {0:['José Santos Cifuentes', 'Manuel Miquel Rodríguez', 'Gaspar del Río Peña', 'Pascual Achurra Valero'], 
                        1:['Justo Donoso Vivanco', 'Pedro García de la Huerta Saravia']}[rep]
        reemplazantes = {0:['Manuel Miquel'], 1:['^$']}[rep]
        reemplazados = {0:['Agustín Edwards Ossandón', 'Manuel Andrés Orrego'], 1:['^$']}[rep] #reemplazados en valparaiso
        
        if (rep == 0):
            candidatos.loc[candidatos['Candidatos'] == 'Rafael Sotomayor Baeza', ['Distrito', 'Electos']] = ['Cauquenes', '*']
            
            if not sum(candidatos['Candidatos'].str.contains('Andrés Chacón Barri')):
                candidatos.loc[len(candidatos.index),:] = 'Itata','','Andrés Chacón Barri','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Andrés_Chacón_Barri'
                #
                candidatos.loc[len(candidatos.index),:] = 'Chillán','','Justo Arteaga Alemparte','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Justo_Arteaga_Alemparte'
                candidatos.loc[len(candidatos.index),:] = 'San Carlos','','Jorge Segundo Huneeus Zegers','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Jorge_Segundo_Huneeus_Zegers'
                candidatos.loc[len(candidatos.index),:] = 'Castro','','Alejandro Fierro Pérez de Camino','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Alejandro_Fierro_Pérez_de_Camino'
        else:
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Francisco Antonio Pinto Díaz', 'Juan Agustín Alcalde Bascuñán', 
                                                                    'Victorino Garrido', 'Santiago Salas Palazuelos',
                                                                    'José Santiago Aldunate Toro', 'Marcos Maturana del Campo', 'Manuel Alcalde Velasco', 'Patricio Larraín Gandarillas'])]
            
            candidatos.loc[candidatos['Candidatos'].isin(['Pedro García de la Huerta Saravia']), 'Circunscripción'] = 'Nacional-2' 
            candidatos.loc[candidatos['Candidatos'].isin(['Justo Donoso Vivanco']), 'Circunscripción'] = 'Nacional-3' 
            
    if eleccion == 1858:
        # DIPUTADOS
        # nacimiento: no hay suplente, pero Urzúa-Valenzuela (p.169) señala a Luis Cousiño como ganador.
        # valdivia: id. con rafael pérez de arce

        propietarios = {0:['Manuel Antonio Matta Goyenechea', 'Teodosio Cuadros', 'José Agustín Errázuriz Salas', 'Juan José Pérez Vergara', 'Vicente Varas de la Barra'], 
                        1:['Manuel José Cerda Campos']}[rep]

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('José Santiago Gandarillas Guzmán')):
            candidatos.loc[len(candidatos.index),:] = 'Santiago','','José Santiago Gandarillas Guzmán','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Santiago_Gandarillas_Guzmán'
            candidatos.loc[len(candidatos.index),:] = 'Santiago','','Manuel Antonio Briceño Ibáñez','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Manuel_Antonio_Briceño_Ibáñez'
            candidatos.loc[len(candidatos.index),:] = 'Nacimiento','','Luis Cousiño Squella','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Luis_Cousiño_Squella'
            candidatos.loc[len(candidatos.index),:] = 'Valdivia','','Rafael Pérez de Arce','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Rafael_Pérez_de_Arce'
        else:            
            candidatos = candidatos[~candidatos['Candidatos'].isin(['José Miguel Arístegui Aróstegui', 'José Santiago Aldunate Toro', 'Justo Donoso Vivanco', 'Manuel Alcalde Velasco', 'Manuel Hipólito Riesco Medina', 'Nicolás Larraín Rojas', 'Patricio Larraín Gandarillas', 'Santiago Salas Palazuelos', 'Roberto Simpson Simpson', 'Victorino Garrido'])]
            
            candidatos.loc[candidatos['Candidatos'].isin(['Manuel José Cerda Campos']), 'Circunscripción'] = 'Nacional-1' 
            candidatos.loc[candidatos['Candidatos'].isin(['Manuel Echeverría Larraín', 'Manuel José Balmaceda Ballesteros']), 'Circunscripción'] = 'Nacional-2'             
            
    if eleccion == 1855:
        propietarios = {0:['Manuel Antonio Briceño Ibáñez', 'Ramón González Concha'], 
                        1:['José Miguel Arístegui Aróstegui']}[rep]
        reemplazantes = {0:['^$'], 1:['Victorino Garrido']}[rep]

        if (rep == 0):
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Manuel Andrés Orrego'])] #no se presentó
                
            candidatos.loc[candidatos['Candidatos'] == 'Manuel Antonio Tocornal Grez', ['Distrito', 'Electos']] = ['La Victoria', '*']
            candidatos.loc[candidatos['Candidatos'] == 'José Eugenio Vergara Galeas', ['Distrito', 'Electos']] = ['Chillán', '*']
        else:
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Santiago Echevers Santelices',
                                                                    'José Tadeo Mancheño Lazo de la Vega', 'Justo Donoso Vivanco', 'Manuel Hipólito Riesco Medina', 'Manuel Echeverría Larraín', 'Manuel José Balmaceda Ballesteros', 'Nicolás Larraín Rojas'])]
            
            candidatos.loc[candidatos['Candidatos'] == 'José Miguel Arístegui Aróstegui', 'Circunscripción'] = 'Nacional-3' #suplente electo 
            candidatos.loc[candidatos['Candidatos'] == 'Patricio Larraín Gandarillas', 'Circunscripción'] = 'Nacional-3' 
            
    if eleccion == 1852:
        propietarios = {0:['José Nicolás Tocornal Velasco', 'Manuel José Cerda Campos', 'José Ignacio Larraín Landa', 'Manuel Jerónimo Urmeneta García', 'José Santiago Gandarillas Guzmán', 'Francisco de Borja Eguiguren Urrejola'], 
                        1:['Ramón de la Cavareda Trucíos']}[rep]
        
        if (rep == 0):
            candidatos.loc[candidatos['Candidatos'] == 'José Manuel Hurtado', ['Distrito', 'Electos']] = ['Linares', '*']
            candidatos.loc[candidatos['Candidatos'] == 'José Eugenio Vergara Galeas', ['Distrito', 'Electos_comp']] = ['Quillota', '*']

            if not sum(candidatos['Candidatos'].str.contains('Valentín Marcoleta Dávila')):
                candidatos.loc[len(candidatos.index),:] = 'Putaendo','','Valentín Marcoleta Dávila','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Valentín_Marcoleta_Dávila'
        else:
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Juan de Dios Vial del Río', 'Patricio Larraín Gandarillas'])]

            candidatos.loc[candidatos['Candidatos'] == 'Ramón de la Cavareda Trucíos', 'Circunscripción'] = 'Nacional-3' #suplente electo 

            #suplentes
            candidatos.loc[candidatos['Candidatos'].isin(['José Ángel Ortúzar Formas', 'Francisco de Borja García-Huidobro Aldunate', 'Pedro García de la Huerta Saravia']), 'Circunscripción'] = 'Nacional-1'
            candidatos.loc[candidatos['Candidatos'].isin(['Santiago Salas Palazuelos', 'Roberto Simpson Simpson']), 'Circunscripción'] = 'Nacional-2'
            candidatos.loc[candidatos['Candidatos'].isin(['Nicolás Larraín Rojas', 'Manuel Hipólito Riesco Medina', 'José Miguel Arístegui Aróstegui']), 'Circunscripción'] = 'Nacional-3'

            if not sum(candidatos['Candidatos'].str.contains('José Tadeo Mancheño Lazo de la Vega')):
                candidatos.loc[len(candidatos.index),:] = 'Nacional-2','','José Tadeo Mancheño Lazo de la Vega','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Tadeo_Mancheño_Lazo_de_la_Vega'

    if eleccion == 1849:
        propietarios = {0:['Diego Echeverría Larraín', 'Antonio Vidal Pizarro', 'Vicente Ramón Sanfuentes Torres'], 
                        1:['Ramón de la Cavareda Trucíos', 'Ramón Subercaseaux Mercado']}[rep]
        
        if (rep == 0):
            candidatos.loc[candidatos['Candidatos'] == 'Pedro Nolasco Vidal Gómez', ['Distrito', 'Electos']] = ['Chillán', '*']
            candidatos.loc[candidatos['Candidatos'] == 'Juan Bello Dunn', ['Distrito', 'Electos']] = ['Los Ángeles', '*']

            if not sum(candidatos['Candidatos'].str.contains('Manuel Montt Torres')):
                candidatos.loc[len(candidatos.index),:] = 'Casablanca','','Ambrosio Olivos Gómez','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Ambrosio_Olivos_Gómez'
                candidatos.loc[len(candidatos.index),:] = 'Santiago','','Manuel Montt Torres','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Manuel_Montt_Torres'
                #
                candidatos.loc[len(candidatos.index),:] = 'Valparaíso','','Francisco Salvador Alvares Pérez','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Francisco_Salvador_Alvares_Pérez'
                candidatos.loc[len(candidatos.index),:] = 'Santiago','','José María Eyzaguirre Larraín','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_María_Eyzaguirre_Larraín'
                candidatos.loc[len(candidatos.index),:] = 'Santiago','','Domingo Matte Messía','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Domingo_Matte_Messía'
                candidatos.loc[len(candidatos.index),:] = 'Santiago','','Antonio de Toro Irarrazával','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Antonio_de_Toro_Irarrazával'
        else:
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Mariano Egaña Fabres', 'José Manuel Ortúzar Formas', 'José Miguel Arístegui Aróstegui', 'Manuel Rengifo Cárdenas'])] 
            
            candidatos.loc[candidatos['Candidatos'] == 'Ramón de la Cavareda Trucíos', 'Circunscripción'] = 'Nacional-3' #suplente electo 
            candidatos.loc[candidatos['Candidatos'] == 'Ramón Subercaseaux Mercado', 'Circunscripción'] = 'Nacional-3' #suplente electo 

            if not sum(candidatos['Candidatos'].str.contains('Santiago Echevers Santelices')):
                candidatos.loc[len(candidatos.index),:] = 'Nacional-1','','Santiago Echevers Santelices','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Santiago_de_Etcheverz_Santelices'
            
    if eleccion == 1846:
        propietarios = {0:['Carlos Formas Urízar', 'Luis de la Cruz Goyeneche', 'Ignacio Reyes Saravia', 'José Agustín Seco Santa Cruz'], 
                        1:['Ramón de la Cavareda Trucíos']}[rep]

        if (rep == 0):
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Ambrosio Olivos Gómez', 'José María Eyzaguirre Larraín', 'Antonio de Toro Irarrazával'])]
        
            candidatos.loc[candidatos['Candidatos'] == 'Pedro Francisco Lira Argomedo', ['Distrito', 'Electos']] = ['San Fernando', '*']
            candidatos.loc[candidatos['Candidatos'] == 'Antonio García Reyes', ['Distrito', 'Electos']] = ['Los Ángeles', '*']        
        
            if not sum(candidatos['Candidatos'].str.contains('Manuel Montt Torres')):
                candidatos.loc[len(candidatos.index),:] = 'Petorca','','Manuel Montt Torres','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Manuel_Montt_Torres'
        else:
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Manuel Rengifo Cárdenas', 'Rafael Correa de Saa Lazón'])] 

            candidatos.loc[candidatos['Candidatos'] == 'Ramón de la Cavareda Trucíos', 'Circunscripción'] = 'Nacional-3' #suplente electo 

            if not sum(candidatos['Candidatos'].str.contains('Francisco Ignacio Ossa Mercado')):
                candidatos.loc[len(candidatos.index),:] = 'Nacional-2','','Francisco Ignacio Ossa Mercado','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Francisco_Ignacio_Ossa_Mercado'
                                    
    if eleccion == 1843:       
        propietarios = {0:['José Tomás Gallo Goyenechea', 'Miguel Dávila Silva', 'José Gabriel Palma Villanueva', 'Ramón Tagle Echeverría'], 1:['^$']}[rep]
        
        if (rep == 0):
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Antonio Prado Sotta'])] #no concurrió
        
            candidatos.loc[candidatos['Candidatos'] == 'José Santiago Gandarillas Guzmán', ['Distrito', 'Electos']] = ['Valdivia', '*']
            candidatos.loc[candidatos['Candidatos'] == 'José Victorino Lastarria Santander', ['Distrito', 'Electos_comp']] = ['Parral', '*']
        
            if not sum(candidatos['Candidatos'].str.contains('Manuel Montt Torres')):
                candidatos.loc[len(candidatos.index),:] = 'Petorca','','Manuel Montt Torres','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Manuel_Montt_Torres'
                candidatos.loc[len(candidatos.index),:] = 'Santiago','','Ramón Errázuriz Aldunate','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Ramón_De_Errázuriz_Aldunate'
                candidatos.loc[len(candidatos.index),:] = 'Santiago','','Ambrosio Aldunate Carvajal','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Ambrosio_Aldunate_Carvajal'
                candidatos.loc[len(candidatos.index),:] = 'Santiago','','Pedro García de la Huerta Saravia','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Pedro_García_de_la_Huerta_Saravia'
        else:
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Rafael Correa de Saa Lazón', 'Diego Portales Palazuelos'])] 
 
    if eleccion == 1840:
        propietarios = {0:['Manuel Covarrubias Ortúzar', 'Miguel del Fierro Illanes', 'Manuel José Cerda Campos'], 
                        1:['Ramón de la Cavareda Trucíos']}[rep]        
        presuntivos = {0:['José del Rosario Jiménez', 'Juan Gregorio de las Heras de la Gacha'], 1:['^$']}[rep]

        if (rep == 0):
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Joaquín Manuel Gutiérrez Bustamante'])]
        
            candidatos.loc[candidatos['Candidatos'] == 'Miguel Dávila Silva', ['Distrito', 'Electos']] = ['Santiago', '*']
            candidatos.loc[candidatos['Candidatos'] == 'Ramón Rozas Rozas', ['Distrito', 'Electos']] = ['Cauquenes', '*']
            candidatos.loc[candidatos['Candidatos'] == 'Ramón Francisco Rozas Mendiburú', ['Distrito', 'Electos']] = ['Lautaro', '*'] #rozas urrutia
            candidatos.loc[candidatos['Candidatos'] == 'Antonio Prado Sotta', ['Distrito', 'Electos']] = ['Valdivia', '*'] #prado de la sotta
        
            if not sum(candidatos['Candidatos'].str.contains('Manuel Montt Torres')):
                candidatos.loc[len(candidatos.index),:] = 'Valparaíso','','Manuel Montt Torres','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Manuel_Montt_Torres'
                #            
                candidatos.loc[len(candidatos.index),:] = 'San Fernando','','José Miguel de los Ríos Lizardi','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Miguel_De_los_Ríos_Lizardi'        
        else:
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Diego Portales Palazuelos', 'Fernando Antonio Elizalde Marticorena', 'Manuel Rengifo Cárdenas', 'Agustín Vial Santelices'])] 

            candidatos.loc[candidatos['Candidatos'] == 'Ramón de la Cavareda Trucíos', 'Circunscripción'] = 'Nacional-2' #suplente electo 
                
    if eleccion == 1837:        
        # DIPUTADOS
        # Vicente Iñíguez, suplente por Santiago y Melipilla 
        # Buenaventura Marín, suplente por Santiago y Quillota

        propietarios = {0:['Carlos Formas Urízar', 'José Agustín Seco Santa Cruz', 'Manuel Covarrubias Ortúzar', 'Pedro Nolasco Mena Ramírez-Rivilla', 'Francisco Javier Valdés Aldunate', 
                           'Francisco Javier Riesco Medina', 'Vicente Ortúzar Formas', 'José María Concha Vergara', 'Manuel González Ortúzar', 'Domingo Matte Messía', 
                           'Rafael Gatica Soiza', 'Santiago Pérez Matta'], 1:['^$']}[rep]

        if (rep == 0):    
            candidatos.loc[candidatos['Candidatos'] == 'Victorino Garrido', ['Distrito', 'Electos']] = ['Valparaíso', '*'] 
            candidatos.loc[candidatos['Candidatos'] == 'José Vicente Izquierdo Jaraquemada', ['Distrito', 'Electos']] = ['Santiago', '*'] 
            candidatos.loc[candidatos['Candidatos'] == 'Domingo Eyzaguirre Arechavala', ['Distrito', 'Electos']] = ['Talca', '*'] 
            candidatos.loc[candidatos['Candidatos'] == 'Antonio Garfias Patiño', ['Distrito', 'Electos']] = ['Puchacay', '*'] 
            candidatos.loc[candidatos['Candidatos'] == 'Joaquín Tocornal Jiménez', ['Distrito', 'Electos']] = ['Concepción', '*'] 
            candidatos.loc[candidatos['Candidatos'] == 'Antonio de Toro Irarrázaval', ['Distrito', 'Electos']] = ['Los Ángeles', '*']         
    
            candidatos.loc[len(candidatos.index),:] = 'Quillota','','Juan Buenaventura Marín Recabarren','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Buenaventura_(Ventura)_Marín_Recabarren'
            candidatos.loc[len(candidatos.index),:] = 'Santiago','','Juan Buenaventura Marín Recabarren','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Buenaventura_(Ventura)_Marín_Recabarren'
            candidatos.loc[len(candidatos.index),:] = 'Melipilla','','Vicente Iñíguez Landa','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Vicente_Iñiguez_Landa'
        else:
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Diego Portales Palazuelos' ,'Ramón de la Cavareda Trucíos'])] 

            if not sum(candidatos['Candidatos'].str.contains('Estanislao Segundo Portales Larraín')):
                candidatos.loc[len(candidatos.index),:] = 'Nacional-1','','Estanislao Segundo Portales Larraín','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Estanislao_Segundo_Portales_Larraín'

    if eleccion == 1834:
        # DIPUTADOS
        # Santiago Mardones, suplente por Copiapó y Putaendo 
        # José Santiago de Toro Irarrázaval, suplente por San Felipe y Rancagua, propietario por Chillán en complementaria (1836)
        # Antonio vidal, doble suplente por Melipilla y San Fernando
                
        propietarios = {0:['Ignacio Reyes Saravia', 'Francisco Javier Riesco Medina', 'José Vicente Arlegui Rodríguez'], 1:['^$']}[rep]        
        presuntivos = {0:['Rafael Gatica Soiza'], 1:['^$']}[rep]

        if (rep == 0):
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Jorge Edwards Brown'])] #no concurrió

            candidatos.loc[candidatos['Candidatos'] == 'Diego Arriarán del Río', ['Distrito', 'Electos']] = ['Santiago', '*']
            candidatos.loc[candidatos['Candidatos'] == 'José Antonio Rosales Mercado', ['Distrito', 'Electos']] = ['Santiago', '*']
            candidatos.loc[candidatos['Candidatos'] == 'Miguel del Fierro Illanes', ['Distrito', 'Electos']] = ['Rancagua', '*']   
            candidatos.loc[candidatos['Candidatos'] == 'Manuel Barros Andonaegui', ['Distrito', 'Electos']] = ['Curicó', '*']            
            candidatos.loc[candidatos['Candidatos'] == 'Eugenio Domingo Torres Velasco', ['Distrito', 'Electos']] = ['Cauquenes', '*']
            candidatos.loc[candidatos['Candidatos'] == 'Antonio Garfias Patiño', ['Distrito', 'Electos']] = ['Puchacay', '*']
            candidatos.loc[candidatos['Candidatos'] == 'Antonio de Toro Irarrázaval', ['Distrito', 'Electos']] = ['Los Ángeles', '*']

            if not sum(candidatos['Candidatos'].str.contains('José Agustín Valdés Saravia')):
                candidatos.loc[len(candidatos.index),:] = 'Cauquenes','','José Agustín Valdés Saravia','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Agustín_Valdés_Saravia'
                #
                candidatos.loc[len(candidatos.index),:] = 'Putaendo','','Santiago Mardones Valenzuela','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Santiago_Mardones_Valenzuela'
                candidatos.loc[len(candidatos.index),:] = 'Rancagua','','José Santiago de Toro Irarrázaval','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Santiago_de_Toro_Irarrázaval'
                candidatos.loc[len(candidatos.index),:] = 'San Fernando','','Antonio Vidal Pizarro','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Antonio_Vidal_Pizarro'
                candidatos.loc[len(candidatos.index),:] = 'Cauquenes','','Agustín Valero Denos','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Agustín_Valero_Denos'
                candidatos.loc[len(candidatos.index),:] = 'Castro','','José Antonio del Pedregal Cerda','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Antonio_Del_Pedregal_Cerda'
                candidatos.loc[len(candidatos.index),:] = 'Quinchao','','Miguel Francisco Trucíos Salas','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Miguel_Francisco_Trucios_Salas'
        else:
            if not sum(candidatos['Candidatos'].str.contains('Santiago Echevers Santelices')):
                candidatos.loc[len(candidatos.index),:] = 'Nacional-1','','Santiago Echevers Santelices','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Santiago_de_Etcheverz_Santelices'
                candidatos.loc[len(candidatos.index),:] = 'Nacional-1','','José Gabriel Tocornal Jiménez','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Gabriel_Tocornal_Jiménez'
                    
    if eleccion == 1831:
        # DIPUTADOS
        # José Ignacio Eyzaguirre, suplente por Castro y Ancud
                
        propietarios = {0:['Rafael Valentín Valdivieso Zañartu', 'Joaquín Manuel Gutiérrez Bustamante', 'José Ángel Ortúzar Formas', 'José Vicente Bustillos Mazeira', 'José María Silva Cienfuegos',
                           'José María Guzmán Ibáñez', 'Antonio Garfias Patiño', 'Manuel Carvallo Gómez'], 
                        1:['^$']}[rep]        
        presuntivos = {0:['José Miguel Infante Rojas', 'Nicolás Pradel Fernández'], 1:['^$']}[rep]

        if (rep == 0):
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Manuel José Gandarillas Guzmán', 'Mariano Egaña Fabres', 'Agustín Vial Santelices', 'Fernando Antonio Elizalde Marticorena',  #optó por el senado 
                                                                    'Pedro Trujillo Zañartu', 'Juan Antonio Guerrero Gayón de Celis', #no se incorporó
                                                                    'Diego José Benavente Bustamante', #renunció
                                                                    'Juan Félix de Alvarado Luque', 'Rafael Gómez Campillo', 'José María Corbalán', 'Andrés Peña y Lillo', 'Juan Agustín Lavín' #asambleas provinciales
                                                                    ])]
    
            candidatos.loc[candidatos['Candidatos'] == 'Clemente Pérez Montt', ['Distrito', 'Electos']] = ['Santiago', '*']
            candidatos.loc[candidatos['Candidatos'] == 'Juan José Urivi Rivas', ['Distrito', 'Electos','Electos_comp']] = ['Itata', None, '*']
                    
            candidatos.loc[candidatos['Candidatos'] == 'Pedro José Lira Argomedo', ['Electos']] = [None]           

            if not sum(candidatos['Candidatos'].str.contains('Manuel José Silva Cabanillas')):
                candidatos.loc[len(candidatos.index),:] = 'Petorca','','Manuel José Silva Cabanillas','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Manuel_José_De_Silva_Cabanillas'
                candidatos.loc[len(candidatos.index),:] = 'Aconcagua','','José Manuel Astorga Camus','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Manuel_de_Astorga_Camus'
                candidatos.loc[len(candidatos.index),:] = 'San Fernando','','Francisco Javier Ovalle','','','','*','*',''
                candidatos.loc[len(candidatos.index),:] = 'San Fernando','','Estanislao Segundo Portales Larraín','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Estanislao_Segundo_Portales_Larraín'
                candidatos.loc[len(candidatos.index),:] = 'Curicó','','Fernando Márquez de la Plata Encalada','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Fernando_Márquez_de_la_Plata_Encalada'
                candidatos.loc[len(candidatos.index),:] = 'San Carlos','','Juan Francisco Larraín Rojas','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Francisco_Larraín_Rojas'
                candidatos.loc[len(candidatos.index),:] = 'Concepción','','Antonio Jacobo Vial Formas','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Antonio_Jacobo_Vial_Formas'
                #
                candidatos.loc[len(candidatos.index),:] = 'Petorca','','Juan Bautista García','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Bautista_García'
                candidatos.loc[len(candidatos.index),:] = 'San Fernando','','José Antonio Huici Trucíos','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Antonio_De_Huici_Trucíos'
                candidatos.loc[len(candidatos.index),:] = 'Los Ángeles','','Juan Agustín Alcalde Bascuñán','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Agustín_Alcalde_Bascuñán'              
                candidatos.loc[len(candidatos.index),:] = 'Valdivia','','Ignacio Reyes Saravia','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Ignacio_Reyes_Saravia'
                candidatos.loc[len(candidatos.index),:] = 'Ancud','','José Ignacio Eyzaguirre Arechavala','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Ignacio_Eyzaguirre_Arechavala'
        else:
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Pedro Alcántara Urriola Balbontín', 'José Antonio Rodríguez Aldea', 'Diego José Benavente Bustamante',
                                                                    'Juan de Dios Vial del Río'])]            
            
    if eleccion == 1829:
        # DIPUTADOS
        # Bernardo Caceres, suplente por Lautaro y Concepción
        # Pedro Félix Vicuña, suplente por Elqui, Quillota e Itata
        
        propietarios = {0:['Nicolás Larraín Aguirre', 'Juan de Dios Pérez de Valenzuela Torrealba', 'José Antonio Zúñiga', 'Vicente Claro Montenegro', 'José María Fernández del Río', 'José Antonio Argomedo González', 'Pedro Chacón Morales'], 1:['^$']}[rep]
        reemplazados = {0:['^$'], 1:['Juan Antonio Guerrero Gayón de Celis']}[rep]
        reemplazantes = {0:['^$'], 1:['José Gaspar Marín Esquivel']}[rep]

        if (rep == 0):
            candidatos = candidatos[~candidatos['Candidatos'].isin(['José Joaquín Echeverría Larraín', 'José Antonio Rivero', 'Diego Carvallo Matta',  #no pudo presentarse
                                                                    'José Ignacio Izquierdo Jaraquemada', 'Martín de Orjera', #optó por el senado
                                                                    'Pedro Moreno', 'José María Poblete', 'Clemente Lantaño del Pino', 'Vicente Fernández', 'Raimundo Prado', 'Juan Agustín Lavín', 'José María Urrutia Ibáñez', 'Ignacio Cerda', 'Santiago Fernández Barriga', 'Julián Jarpa Caamaño' #asambleas provinciales
                                                                    ])]         
    
            candidatos.loc[candidatos['Candidatos'] == 'José Fermín del Solar Marín', ['Distrito', 'Electos']] = ['Illapel', '*']
            candidatos.loc[candidatos['Candidatos'] == 'Pedro Nolasco Mena Ramírez-Rivilla', ['Distrito', 'Electos']] = ['Quillota', '*']
            candidatos.loc[candidatos['Candidatos'] == 'Rafael Bilbao Beyner', ['Distrito', 'Electos']] = ['Santiago', '*']        
            candidatos.loc[candidatos['Candidatos'] == 'José Santiago Sánchez Alfaro', ['Distrito', 'Electos']] = ['Cauquenes', '*']
                    
            #Ancud se llamaba «San Carlos»
            candidatos.loc[candidatos['Candidatos'].isin(['José Ignacio Vargas', 'Benigno Téllez']), 'Distrito'] = 'Ancud'
    
            if not sum(candidatos['Candidatos'].str.contains('Francisco Osorio')):            
                # Elqui: Urzúa-Valenzuela, p38
                candidatos.loc[len(candidatos.index),:] = 'Elqui','','Santiago Segundo Pérez Larraín','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Santiago_Segundo_Pérez_Larraín' 
                candidatos.loc[len(candidatos.index),:] = 'Elqui','','Francisco Osorio','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Francisco_Osorio'
                candidatos.loc[len(candidatos.index),:] = 'San Fernando','','José Tomás Argomedo González','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Tomás_Argomedo_González'
                candidatos.loc[len(candidatos.index),:] = 'San Fernando','','Fermín Fuentes Ramírez','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Fermín_Fuentes_Ramírez'
                candidatos.loc[len(candidatos.index),:] = 'Curicó','','Agustín Aldea','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Agustín_De_Aldea'
                candidatos.loc[len(candidatos.index),:] = 'Rere','','José Gregorio Meneses Guerrero','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Gregorio_Meneses_Guerrero'            
                candidatos.loc[len(candidatos.index),:] = 'Lautaro','','Juan Ignacio Benítez','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Ignacio_Benítez'
                candidatos.loc[len(candidatos.index),:] = 'Osorno','','Miguel Cosme Pérez de Arce Henríquez','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Miguel_Cosme_Pérez_de_Arce_Henríquez'
                candidatos.loc[len(candidatos.index),:] = 'Ancud','','José Ignacio Vargas','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Ignacio_Vargas'
                #
                candidatos.loc[len(candidatos.index),:] = 'Elqui','','Pedro Félix Vicuña Aguirre','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Pedro_Félix_Vicuña_Aguirre' 
                candidatos.loc[len(candidatos.index),:] = 'Itata','','Pedro Félix Vicuña Aguirre','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Pedro_Félix_Vicuña_Aguirre'
                candidatos.loc[len(candidatos.index),:] = 'Quillota','','Pedro Félix Vicuña Aguirre','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Pedro_Félix_Vicuña_Aguirre'
                candidatos.loc[len(candidatos.index),:] = 'Aconcagua','','José María Tocornal Jiménez','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_María_Tocornal_Jiménez' #fuente: Urzúa-Valenzuela, p.39
                candidatos.loc[len(candidatos.index),:] = 'Linares','','José Manuel Astorga Camus','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Manuel_de_Astorga_Camus'
                candidatos.loc[len(candidatos.index),:] = 'Lautaro','','José Bernardo Cáceres Gutiérrez de Palacios','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Bernardo_Cáceres_Gutiérrez_de_Palacios'
                candidatos.loc[len(candidatos.index),:] = 'Los Ángeles','','Antonio Gundián Padilla','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Antonio_Gundián_Padilla'
                candidatos.loc[len(candidatos.index),:] = 'Quinchao','','José Manuel Feliú Rogells','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Manuel_Olaguer_Feliú_y_Rogells'
        else:
            candidatos.loc[candidatos['Candidatos'].isin(['Francisco Fernández', 'José Ignacio Izquierdo Jaraquemada']), 'Circunscripción'] = 'Santiago'

            candidatos = candidatos[~candidatos['Circunscripción'].isin(['Maule', 'Concepción'])]
            
    if eleccion == 1828:
        propietarios = {0:['Rafael Bilbao Beyner', 'Juan Buenaventura Marín Recabarren', 'Manuel Sotomayor Elso', 'José Gregorio Meneses Guerrero', 'Bruno Larraín Aguirre', 
                           'Melchor José de Ramos Font', 'Juan Cortés', 'Miguel Ureta Carrera', 'Manuel Antonio Araoz Carrera'], 
                        1:['^$']}[rep]

        if (rep == 0):
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Francisco Ramón Vicuña Larraín', 'José Gaspar Marín Esquivel', 'Pedro Felipe Iñiguez Landa', 'Joaquín Ramírez de la Saldaña Velasco', 'Pedro José Prado Montaner',
                                                                    'Manuel Antonio González Valenzuela', 'José Miguel del Solar Marín', 'José Antonio Huici Trucíos', 'Pedro Félix Vicuña Aguirre', 'Manuel Gormaz Lisperguer',
                                                                    'Francisco Fernández', 'José María García', 'José Ignacio Sánchez Peña', 'Juan de Dios Vial del Río', 'José Antonio Ovalle Vivar',
                                                                    'José María Palacios', 'Pedro José Lira Argomedo', 'Manuel Valledor Blanco', 'Juan Garcés Vargas', 'José Manuel Barros Fernández',
                                                                    'Casimiro Albano Pereira de la Cruz', 'Juan Antonio Bauzá', 'José Joaquín Prieto Vial', 'José María Vásquez de Novoa López de Artigas',
                                                                    'Pedro Antonio Palazuelos Astaburuaga', 'Elías Andrés Guerrero', 'Vicente González Palma', 'Francisco Ruiz-Tagle Portales',
                                                                    'Francisco Calderón Zumelzu', 'Manuel Antonio Recabarren Aguirre', 'José Ignacio Eyzaguirre Arechavala', 'Manuel Magallanes Otero', 
                                                                    'Carlos Rodríguez Erdoyza', 'Eleuterio Andrade Cárcamo', 'Ramón Errázuriz Aldunate', 'Ramón Herrera', 'Nicolás Pradel Fernández', #asambleas provinciales o congreso constituyente de 1828
                                                                    'José Antonio González Palma', 'Juan Fariñas Ugalde', #error
                                                                    'Pedro Nolasco Mena Ramírez-Rivilla', #renunció
                                                                    'Manuel José Gandarillas Guzmán' #no se incorporó
                                                                    ])] 
            
            candidatos.loc[candidatos['Candidatos'] == 'Melchor de Santiago-Concha Cerda', ['Distrito', 'Electos']] = ['Los Andes', '*']
            candidatos.loc[candidatos['Candidatos'] == 'Fernando Antonio Elizalde Marticorena', ['Distrito', 'Electos']] = ['San Carlos', '*']
            candidatos.loc[candidatos['Candidatos'] == 'Agustín López de Alcázar', ['Distrito', 'Electos']] = ['Los Ángeles', '*']
            candidatos.loc[candidatos['Candidatos'] == 'Miguel Collao', ['Distrito', 'Electos']] = ['Los Ángeles', '*']        
            candidatos.loc[candidatos['Candidatos'] == 'José Bernardo Cáceres Gutiérrez de Palacios', ['Distrito', 'Electos']] = ['Lautaro', None]
    
            if not sum(candidatos['Candidatos'].str.contains('Agustín Vial Santelices')):
                candidatos.loc[len(candidatos.index),:] = 'Talca','','José Francisco Gana López','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Francisco_Gana_López'
                candidatos.loc[len(candidatos.index),:] = 'Chillán','','Agustín Vial Santelices','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Agustín_Vial_Santelices'
                candidatos.loc[len(candidatos.index),:] = 'Chillán','','Juan José Gutiérrez Palacios','','','','*','*','' #notar que se trata de juan jose palacios puga
                candidatos.loc[len(candidatos.index),:] = 'Lautaro','','Juan Ignacio Benítez','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Ignacio_Benítez'
                candidatos.loc[len(candidatos.index),:] = 'Los Ángeles','','Venancio Escanilla','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Venancio_Escanilla'            

        else:
            candidatos = candidatos[~candidatos['Candidatos'].isin(['José María Palacios'])]

    candidatos = candidatos.drop_duplicates(subset=[subdivrow,'Candidatos'], keep="last")
    
    candidatos.loc[candidatos['Candidatos'].str.contains('|'.join(propietarios)), 'Electos'] = '*'
    
    return candidatos, reemplazados, reemplazantes, presuntivos, partidos