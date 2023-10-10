#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 16:34:48 2023

@author: sebastian
"""

def correcciones1833_1888(candidatos, eleccion, rep):
    
    candidatos.loc[candidatos['Partido'] == 'Independiente', 'Partido'] = 'Candidatura Independiente'

    reemplazados = {0:['^$'], 1:['^$']}[rep]
    reemplazantes = {0:['^$'], 1:['^$']}[rep]
    presuntivos = {0:['^$'], 1:['^$']}[rep]
    partidos = {'^$': {0:['^$'], 1:['^$']}[rep]}    
    
    """
    En este período hay
    - propietarios que escogieron el Senado (eliminados), 
    - propietarios fallecidos antes de asumir o que simplemente no asumieron (eliminados)
    - propietarios que escogen otra provincia (corregido),
    - suplentes que asumen como propietarios, o propietarios registrados como suplentes en bcn (corregido)
    - suplentes por dos provincias
    """
    propietarios = {0:['^$'], 1:['^$']}[rep]
    
    if eleccion == 1888:
        candidatos.loc[candidatos['Candidatos'] == 'Arturo Maximiano Edwards Ross', ['Distrito', 'Electos']] = ['Cachapoal', '*']

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('José Antonio Valdés González')):
            candidatos.loc[len(candidatos.index),:] = 'La Serena','','José Antonio Valdés González','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Antonio_Valdés_González'

    if eleccion == 1885:
        propietarios = {0:['Nicolás R. Peña Vicuña', 'Liborio Sánchez Cárdenas'], 1:['^$']}[rep]

        candidatos.loc[candidatos['Candidatos'] == 'Vicente Dávila Larraín', ['Distrito', 'Electos']] = ['Concepción', '*']
        candidatos.loc[candidatos['Candidatos'] == 'Luis Martiniano Rodríguez Herrera', ['Distrito', 'Electos']] = ['Quinchao', '*']

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('José Antonio Valdés González')):
            candidatos.loc[len(candidatos.index),:] = 'Combarbalá','','José Antonio Valdés González','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Antonio_Valdés_González'
        
    if eleccion == 1882:
        propietarios = {0:['José Agustín Tagle Montt'], 1:['^$']}[rep]
        presuntivos = {0:['Victorino Rojas Magallanes', 'Nicolás Naranjo Palacios'], 1:['^$']}[rep]
        
    if eleccion == 1879:
        propietarios = {0:['Agustín Segundo Rodríguez Azócar', 'Ramón Ricardo Rozas Garfias'], 1:['^$']}[rep]
        
        candidatos.loc[candidatos['Candidatos'] == 'Aniceto Vergara Albano', ['Distrito', 'Electos']] = ['Chillán', '*'] #en «Anales» aparece como propietario en dos provincias: los andes y chillán (bcn considera esta)
        candidatos.loc[candidatos['Candidatos'] == 'José Francisco Vergara Donoso', ['Distrito', 'Electos']] = ['Quinchao', '*']
        
        candidatos.loc[candidatos['Candidatos'] == 'Justo García', ['Electos']] = [None]        

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('José Clemente Cecilio Fabres')):
            candidatos.loc[len(candidatos.index),:] = 'Santiago','','José Clemente Cecilio Fabres Fernández de Leiva','Partido Conservador','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Clemente_Cecilio_Fabres_Fernández_de_Leiva'
            candidatos.loc[len(candidatos.index),:] = 'Caupolicán','','Raimundo Larraín Covarrubias','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Raimundo_Larraín_Covarrubias'
            candidatos.loc[len(candidatos.index),:] = 'Itata','','Alejandro Fuerro Pérez de Camino','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Alejandro_Fierro_Pérez_de_Camino'
            
    if eleccion == 1876:
        candidatos = candidatos[~candidatos['Candidatos'].isin(['Benjamín Vicuña Mackenna', 'Manuel Jerónimo Urmeneta García'])] #escogieron el senado 

        propietarios = {0:['José Ramón Yávar Jiménez', 'Julio Lecaros Valdés', 'Adolfo Carrasco Albano', 'Juan Eduardo Mackenna Astorga'], 1:['^$']}[rep]

        candidatos.loc[candidatos['Candidatos'] == 'Enrique Cood Ross', ['Distrito', 'Electos']] = ['Melipilla', '*']
                
        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Francisco Prado Aldunate')):
            candidatos.loc[len(candidatos.index),:] = 'Santiago','','Francisco Prado Aldunate','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Francisco_Prado_Aldunate'
            candidatos.loc[len(candidatos.index),:] = 'Santiago','','José Clemente Cecilio Fabres Fernández de Leiva','Partido Conservador','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Clemente_Cecilio_Fabres_Fernández_de_Leiva'

    if eleccion == 1873:
        propietarios = {0:['Ricardo Lecaros Vicuña', 'Fernando Liborio Lazcano Echaurren', 'Juan Esteban Rodríguez Segura'], 1:['^$']}[rep]

        candidatos.loc[candidatos['Candidatos'] == 'Pedro Eulogio Altamirano Aracena', ['Distrito', 'Electos']] = ['Concepción', '*']
        
        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('José Clemente Cecilio Fabres')):
            candidatos.loc[len(candidatos.index),:] = 'Rancagua','','José Clemente Cecilio Fabres Fernández de Leiva','Partido Conservador','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Clemente_Cecilio_Fabres_Fernández_de_Leiva'

    if eleccion == 1870:
        propietarios = {0:['Juan José Cerda', 'Pedro Nolasco Videla Hidalgo', 'Miguel Cruchaga Montt', 'Isidoro Errázuriz Errázuriz', 'Luis Martiniano Rodríguez Herrera'], 1:['^$']}[rep]

        presuntivos = {0:['Ruperto Ovalle Vicuña', 'Pablo Flores', 'José Antonio Soffia Argomedo', 'Miguel Castillo Andueza', #'Marcial Martínez Cuadros', 
                          'Pedro Lucio Cuadra Luque', 'Jovino Novoa Vidal', 'Blas Encinas', 'Manuel Salustio Fernández Pradel', #'Guillermo Matta Goyenechea', 
                          'Ricardo Claro Cruz'], 1:['^$']}[rep]

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

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Francisco de Paula Echaurren González')):
            #existe una confusion entre ambos francisco de paula echaurren
            candidatos.loc[len(candidatos.index),:] = 'Combarbalá','','Francisco de Paula Echaurren González','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Francisco_de_Paula_Echaurren_González'
        
    if eleccion == 1867:
        candidatos = candidatos[~candidatos['Candidatos'].isin(['Pedro Ugarte Ramírez'])] #falleció antes de iniciarse el período
        
        propietarios = {0:['Nicomedes Ossa Cerda', 'José Manuel Pinto Arias', 'Ramón Covarrubias Ortúzar', 'Manuel Amunátegui Aldunate'], 1:['^$']}[rep]

        presuntivos = {0:['Isidoro Errázuriz Errázuriz', 'Jovino Novoa Vidal', 'Guillermo Matta Goyenechea'], 1:['^$']}[rep]
        
        candidatos.loc[candidatos['Candidatos'] == 'Eduardo Montes Solar', ['Electos']] = [None]
        candidatos.loc[candidatos['Candidatos'] == 'Juan de la Cruz Guzmán Guzmán', ['Electos']] = [None]
        candidatos.loc[candidatos['Candidatos'] == 'Ramón Valdés Lecaros', ['Electos']] = [None]
        
        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Juan José Agustín Ugarte Guzmán')):
            candidatos.loc[len(candidatos.index),:] = 'San Fernando','','Juan José Agustín Ugarte Guzmán','Partido Conservador','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_José_Agustín_Ugarte_Guzmán'
            candidatos.loc[len(candidatos.index),:] = 'Constitución','','Juan de Dios Cisternas Moraga','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_de_Dios_Cisternas_Moraga'
            candidatos.loc[len(candidatos.index),:] = 'Constitución','','Antonio Subercaseaux Vicuña','Partido Conservador','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Antonio_Subercaseaux_Vicuña'
            candidatos.loc[len(candidatos.index),:] = 'San Carlos','','Francisco Javier Reyes Cotapos','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Francisco_Javier_Reyes_Cotapos'
    
    if eleccion == 1864:
        candidatos = candidatos[~candidatos['Candidatos'].isin(['Manuel Camilo Vial Formas'])] #va por el senado
        
        propietarios = {0:['Mariano José Ariztía Urmeneta', 'Vicente Izquierdo Urmeneta', 'Adriano Borgoño Vergara', 'Melchor Concha Toro', 'José Francisco Echenique Tagle', 'Miguel Cruchaga Montt', 'Diego Antonio Tagle Echeverría', 'Enrique Cood Ross'], 1:['^$']}[rep]

        presuntivos = {0:['Waldo Silva Algue'], 1:['^$']}[rep]
        
        candidatos.loc[candidatos['Candidatos'] == 'Antonio Varas de la Barra', ['Distrito', 'Electos']] = ['Santiago', '*']
        candidatos.loc[candidatos['Candidatos'] == 'Federico Errázuriz Zañartu', ['Distrito', 'Electos']] = ['Caupolicán', '*']

        candidatos.loc[candidatos['Candidatos'] == 'José Joaquín Blest Gana', ['Distrito', 'Electos_comp']] = ['Chillán', '*']

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Manuel Montt Torres')):
            candidatos.loc[len(candidatos.index),:] = 'Los Andes','','Manuel Montt Torres','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Manuel_Montt_Torres'

    if eleccion == 1861:
        propietarios = {0:['José Santos Cifuentes', 'Manuel Miquel Rodríguez', 'Gaspar del Río Peña', 'Pascual Achurra Valero'], 1:['^$']}[rep]
        
        candidatos.loc[candidatos['Candidatos'] == 'Rafael Sotomayor Baeza', ['Distrito', 'Electos']] = ['Cauquenes', '*']

    if eleccion == 1858:
        # se desconocen los diputados por parral
        # para los ultimos dos suplentes se desconoce el propietario
        propietarios = {0:['Manuel Antonio Matta Goyenechea', 'Teodosio Cuadros', 'José Agustín Errázuriz Salas', 'Juan José Pérez Vergara', 'Vicente Varas de la Barra'], 1:['^$']}[rep]
        
    if eleccion == 1855:
        candidatos = candidatos[~candidatos['Candidatos'].isin(['Manuel Andrés Orrego'])] #no se presentó
        
        propietarios = {0:['Manuel Antonio Briceño Ibáñez', 'Ramón González Concha'], 1:['^$']}[rep]
        
        candidatos.loc[candidatos['Candidatos'] == 'Manuel Antonio Tocornal Grez', ['Distrito', 'Electos']] = ['La Victoria', '*']
        candidatos.loc[candidatos['Candidatos'] == 'José Eugenio Vergara Galeas', ['Distrito', 'Electos']] = ['Chillán', '*']

    if eleccion == 1852:
        propietarios = {0:['José Nicolás Tocornal Velasco', 'Manuel José Cerda Campos', 'José Ignacio Larraín Landa', 'Manuel Jerónimo Urmeneta García', 'José Santiago Gandarillas Guzmán', 'Francisco de Borja Eguiguren Urrejola'], 1:['^$']}[rep]
        
        candidatos.loc[candidatos['Candidatos'] == 'José Manuel Hurtado', ['Distrito', 'Electos']] = ['Linares', '*']
                        
    if eleccion == 1849:
        propietarios = {0:['Diego Echeverría Larraín', 'Antonio Vidal Pizarro', 'Vicente Ramón Sanfuentes Torres'], 1:['^$']}[rep]
        
        candidatos.loc[candidatos['Candidatos'] == 'Pedro Nolasco Vidal Gómez', ['Distrito', 'Electos']] = ['Chillán', '*']
        candidatos.loc[candidatos['Candidatos'] == 'Juan Bello Dunn', ['Distrito', 'Electos']] = ['Los Ángeles', '*']

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Manuel Montt Torres')):
            candidatos.loc[len(candidatos.index),:] = 'Casablanca','','Ambrosio Olivos Gómez','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Ambrosio_Olivos_Gómez'
            candidatos.loc[len(candidatos.index),:] = 'Santiago','','Manuel Montt Torres','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Manuel_Montt_Torres'

    if eleccion == 1846:
        propietarios = {0:['Carlos Formas Urízar', 'Luis de la Cruz Goyeneche', 'Ignacio Reyes Saravia', 'José Agustín Seco Santa Cruz'], 1:['^$']}[rep]
        
        candidatos.loc[candidatos['Candidatos'] == 'Pedro Francisco Lira Argomedo', ['Distrito', 'Electos']] = ['San Fernando', '*']
        candidatos.loc[candidatos['Candidatos'] == 'Antonio García Reyes', ['Distrito', 'Electos']] = ['Los Ángeles', '*']        
        
        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Manuel Montt Torres')):
            candidatos.loc[len(candidatos.index),:] = 'Petorca','','Manuel Montt Torres','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Manuel_Montt_Torres'
        
    if eleccion == 1843:        
        propietarios = {0:['José Tomás Gallo Goyenechea', 'Miguel Dávila Silva', 'José Gabriel Palma Villanueva', 'Ramón Tagle Echeverría'], 1:['^$']}[rep]
                
        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Manuel Montt Torres')):
            candidatos.loc[len(candidatos.index),:] = 'Petorca','','Manuel Montt Torres','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Manuel_Montt_Torres'
            candidatos.loc[len(candidatos.index),:] = 'Santiago','','Ramón Errázuriz Aldunate','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Ramón_De_Errázuriz_Aldunate'
            candidatos.loc[len(candidatos.index),:] = 'Santiago','','Ambrosio Aldunate Carvajal','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Ambrosio_Aldunate_Carvajal'
            candidatos.loc[len(candidatos.index),:] = 'Santiago','','Pedro García de la Huerta Saravia','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Pedro_García_de_la_Huerta_Saravia'
            
    if eleccion == 1840:
        candidatos = candidatos[~candidatos['Candidatos'].isin(['Joaquín Manuel Gutiérrez Bustamante'])]
        
        propietarios = {0:['Manuel Covarrubias Ortúzar', 'Miguel del Fierro Illanes', 'Manuel José Cerda Campos'], 1:['^$']}[rep]        
        presuntivos = {0:['José del Rosario Jiménez', 'Juan Gregorio de las Heras de la Gacha'], 1:['^$']}[rep]

        candidatos.loc[candidatos['Candidatos'] == 'Miguel Dávila Silva', ['Distrito', 'Electos']] = ['Santiago', '*']
        candidatos.loc[candidatos['Candidatos'] == 'Ramón Rozas Rozas', ['Distrito', 'Electos']] = ['Cauquenes', '*']
        candidatos.loc[candidatos['Candidatos'] == 'Ramón Francisco Rozas Mendiburú', ['Distrito', 'Electos']] = ['Lautaro', '*'] #rozas urrutia
        candidatos.loc[candidatos['Candidatos'] == 'Antonio Prado Sotta', ['Distrito', 'Electos']] = ['Valdivia', '*'] #prado de la sotta
        
        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Manuel Montt Torres')):
            candidatos.loc[len(candidatos.index),:] = 'Valparaíso','','Manuel Montt Torres','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Manuel_Montt_Torres'
        
    if eleccion == 1837:
        propietarios = {0:['Carlos Formas Urízar', 'José Agustín Seco Santa Cruz', 'Manuel Covarrubias Ortúzar', 'Pedro Nolasco Mena Ramírez-Rivilla', 'Francisco Javier Valdés Aldunate', 
                           'Francisco Javier Riesco Medina', 'Vicente Ortúzar Formas', 'José María Concha Vergara', 'Manuel González Ortúzar', 'Domingo Matte Messía', 
                           'Rafael Gatica Soiza', 'Santiago Pérez Matta'], 
                        1:['^$']}

        candidatos.loc[candidatos['Candidatos'] == 'Victorino Garrido', ['Distrito', 'Electos']] = ['Valparaíso', '*'] 
        candidatos.loc[candidatos['Candidatos'] == 'José Vicente Izquierdo Jaraquemada', ['Distrito', 'Electos']] = ['Santiago', '*'] 
        candidatos.loc[candidatos['Candidatos'] == 'Domingo Eyzaguirre Arechavala', ['Distrito', 'Electos']] = ['Talca', '*'] 
        candidatos.loc[candidatos['Candidatos'] == 'Antonio Garfias Patiño', ['Distrito', 'Electos']] = ['Puchacay', '*'] 
        candidatos.loc[candidatos['Candidatos'] == 'Joaquín Tocornal Jiménez', ['Distrito', 'Electos']] = ['Concepción', '*'] 
        candidatos.loc[candidatos['Candidatos'] == 'Antonio de Toro Irarrázaval', ['Distrito', 'Electos']] = ['Los Ángeles', '*']         

    if eleccion == 1834:
        propietarios = {0:['Francisco Javier Riesco Medina', 'José Vicente Arlegui Rodríguez'], 1:['^$']}[rep]
        
        presuntivos = {0:['Rafael Gatica Soiza'], 1:['^$']}[rep]
        
        candidatos.loc[candidatos['Candidatos'] == 'Manuel Barros Andonaegui', ['Distrito', 'Electos']] = ['Curicó', '*']    
        candidatos.loc[candidatos['Candidatos'] == 'Diego Arriarán del Río', ['Distrito', 'Electos']] = ['Santiago', '*']
        candidatos.loc[candidatos['Candidatos'] == 'José Antonio Rosales Mercado', ['Distrito', 'Electos']] = ['Santiago', '*']
        candidatos.loc[candidatos['Candidatos'] == 'Miguel del Fierro Illanes', ['Distrito', 'Electos']] = ['Rancagua', '*']   
        candidatos.loc[candidatos['Candidatos'] == 'Eugenio Domingo Torres Velasco', ['Distrito', 'Electos']] = ['Cauquenes', '*']
        candidatos.loc[candidatos['Candidatos'] == 'Antonio Garfias Patiño', ['Distrito', 'Electos']] = ['Puchacay', '*']
        candidatos.loc[candidatos['Candidatos'] == 'Antonio de Toro Irarrázaval', ['Distrito', 'Electos']] = ['Los Ángeles', '*']

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('José Agustín Valdés Saravia')):
            candidatos.loc[len(candidatos.index),:] = 'Cauquenes','','José Agustín Valdés Saravia','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Agustín_Valdés_Saravia'

    if eleccion == 1831:
        candidatos = candidatos[~candidatos['Candidatos'].isin(['Manuel José Gandarillas Guzmán', 'Mariano Egaña Fabres', 'José Antonio Huici Trucíos', 'Agustín Vial Santelices', 'Fernando Antonio Elizalde Marticorena',  #optó por el senado 
                                                                'Pedro Trujillo Zañartu', #no se incorporó
                                                                'Diego José Benavente Bustamante', #renunció
                                                                'Juan Félix de Alvarado Luque', 'Rafael Gómez Campillo', 'José María Corbalán' #asambleas provinciales
                                                                ])]
        
        propietarios = {0:['Rafael Valentín Valdivieso Zañartu', 'Joaquín Manuel Gutiérrez Bustamante', 'José Ángel Ortúzar Formas', 'José Vicente Bustillos Mazeira', 'José María Silva Cienfuegos',
                           'José María Guzmán Ibáñez', 'Antonio Garfias Patiño', 'Manuel Carvallo Gómez'], 
                        1:['^$']}[rep]
        
        presuntivos = {0:['Juan José Urivi Rivas', 'José Miguel Infante Rojas', 'Nicolás Pradel Fernández'], 1:['^$']}[rep]
        
        candidatos.loc[candidatos['Candidatos'] == 'Clemente Pérez Montt', ['Distrito', 'Electos']] = ['Santiago', '*']
        
        candidatos.loc[candidatos['Candidatos'] == 'Pedro José Lira Argomedo', ['Electos']] = [None]           

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Manuel José Silva Cabanillas')):
            candidatos.loc[len(candidatos.index),:] = 'Petorca','','Manuel José Silva Cabanillas','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Manuel_José_De_Silva_Cabanillas'
            candidatos.loc[len(candidatos.index),:] = 'Petorca','','Juan Bautista García','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Bautista_García'
            candidatos.loc[len(candidatos.index),:] = 'Aconcagua','','José Manuel Astorga Camus','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Manuel_de_Astorga_Camus'
            candidatos.loc[len(candidatos.index),:] = 'San Fernando','','Francisco Javier Ovalle','','','','*','*',''
            candidatos.loc[len(candidatos.index),:] = 'San Fernando','','Estanislao Segundo Portales Larraín','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Estanislao_Segundo_Portales_Larraín'
            candidatos.loc[len(candidatos.index),:] = 'Curicó','','Fernando Márquez de la Plata Encalada','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Fernando_Márquez_de_la_Plata_Encalada'
            candidatos.loc[len(candidatos.index),:] = 'San Carlos','','Juan Francisco Larraín Rojas','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Francisco_Larraín_Rojas'
            candidatos.loc[len(candidatos.index),:] = 'Concepción','','Antonio Jacobo Vial Formas','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Antonio_Jacobo_Vial_Formas'
            candidatos.loc[len(candidatos.index),:] = 'Valdivia','','Ignacio Reyes Saravia','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Ignacio_Reyes_Saravia'
            
    if eleccion == 1829:
        candidatos = candidatos[~candidatos['Candidatos'].isin(['José Ignacio Izquierdo Jaraquemada', #optó por el senado
                                                                'Pedro Moreno', 'José María Poblete', 'Clemente Lantaño del Pino', #asambleas provinciales
                                                                ])] 
        
        propietarios = {0:['Nicolás Larraín Aguirre', 'Juan de Dios Pérez de Valenzuela Torrealba', 'José Antonio Zúñiga', 'Vicente Claro Montenegro'], 1:['^$']}[rep]

        candidatos.loc[candidatos['Candidatos'] == 'José Fermín del Solar Marín', ['Distrito', 'Electos']] = ['Illapel', '*']
        candidatos.loc[candidatos['Candidatos'] == 'Pedro Nolasco Mena Ramírez-Rivilla', ['Distrito', 'Electos']] = ['Quillota', '*']
        
        #Ancud se llamaba «San Carlos»
        candidatos.loc[candidatos['Candidatos'].isin(['José Ignacio Vargas', 'Benigno Téllez']), 'Distrito'] = 'Ancud'

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Francisco Osorio')):
            candidatos.loc[len(candidatos.index),:] = 'Aconcagua','','Francisco Osorio','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Francisco_Osorio'
            candidatos.loc[len(candidatos.index),:] = 'San Fernando','','José Tomás Argomedo González','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Tomás_Argomedo_González'
            candidatos.loc[len(candidatos.index),:] = 'San Fernando','','Fermín Fuentes Ramírez','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Fermín_Fuentes_Ramírez'
            candidatos.loc[len(candidatos.index),:] = 'Curicó','','Agustín Aldea','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Agustín_De_Aldea'
            candidatos.loc[len(candidatos.index),:] = 'Rere','','José Gregorio Meneses Guerrero','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Gregorio_Meneses_Guerrero'            
            candidatos.loc[len(candidatos.index),:] = 'Lautaro','','Juan Ignacio Benítez','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Ignacio_Benítez'
            candidatos.loc[len(candidatos.index),:] = 'Osorno','','Miguel Cosme Pérez de Arce Henríquez','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Miguel_Cosme_Pérez_de_Arce_Henríquez'
            
    if eleccion == 1828:
        ##asambleas provinciales o congreso constituyente de 1828
        candidatos = candidatos[~candidatos['Candidatos'].isin(['Francisco Ramón Vicuña Larraín', 'José Gaspar Marín Esquivel', 'Pedro Felipe Iñiguez Landa', 'Joaquín Ramírez de la Saldaña Velasco', 'Pedro José Prado Montaner',
                                                                'Manuel Antonio González Valenzuela', 'José Miguel del Solar Marín', 'José Antonio Huici Trucíos', 'Pedro Félix Vicuña Aguirre', 'Manuel Gormaz Lisperguer',
                                                                'Francisco Fernández', 'José María García', 'José Ignacio Sánchez Peña', 'Juan de Dios Vial del Río', 'José Antonio Ovalle Vivar',
                                                                'José María Palacios', 'Pedro José Lira Argomedo', 'Manuel Valledor Blanco', 'Juan Garcés Vargas', 'José Manuel Barros Fernández',
                                                                'Casimiro Albano Pereira de la Cruz', 'Juan Antonio Bauzá', 'José Joaquín Prieto Vial', 'José María Vásquez de Novoa López de Artigas',
                                                                'Pedro Antonio Palazuelos Astaburuaga', 'Elías Andrés Guerrero', 'Vicente González Palma', 'Francisco Ruiz-Tagle Portales',
                                                                'Francisco Calderón Zumelzu', 'Manuel Antonio Recabarren Aguirre', 'José Ignacio Eyzaguirre Arechavala', 'Manuel Magallanes Otero', 
                                                                'Carlos Rodríguez Erdoyza', 'Eleuterio Andrade Cárcamo', 'Ramón Errázuriz Aldunate', 'Ramón Herrera', 'Nicolás Pradel Fernández',

                                                                'José Antonio González Palma', 'Juan Fariñas Ugalde', #error
                                                                'Pedro Nolasco Mena Ramírez-Rivilla' #renunció
                                                                ])] 

        propietarios = {0:['Rafael Bilbao Beyner', 'Juan Buenaventura Marín Recabarren', 'Manuel Sotomayor Elso', 'José Gregorio Meneses Guerrero', 'Bruno Larraín Aguirre', 
                           'Melchor José de Ramos Font', 'Juan Cortés', 'Miguel Ureta Carrera', 'Manuel Antonio Araoz Carrera'], 1:['^$']}[rep]
                
        candidatos.loc[candidatos['Candidatos'] == 'Melchor de Santiago-Concha Cerda', ['Distrito', 'Electos']] = ['Los Andes', '*']
        candidatos.loc[candidatos['Candidatos'] == 'Fernando Antonio Elizalde Marticorena', ['Distrito', 'Electos']] = ['San Carlos', '*']
        candidatos.loc[candidatos['Candidatos'] == 'Agustín López de Alcázar', ['Distrito', 'Electos']] = ['Los Ángeles', '*']
        candidatos.loc[candidatos['Candidatos'] == 'Miguel Collao', ['Distrito', 'Electos']] = ['Los Ángeles', '*']        
        candidatos.loc[candidatos['Candidatos'] == 'José Bernardo Cáceres Gutiérrez de Palacios', ['Distrito', 'Electos']] = ['Lautaro', None]

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Agustín Vial Santelices')):
            candidatos.loc[len(candidatos.index),:] = 'Talca','','José Francisco Gana López','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Francisco_Gana_López'
            candidatos.loc[len(candidatos.index),:] = 'Chillán','','Agustín Vial Santelices','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Agustín_Vial_Santelices'
            candidatos.loc[len(candidatos.index),:] = 'Chillán','','Juan José Gutiérrez Palacios','','','','*','*','' #notar que se trata de juan jose palacios puga
            candidatos.loc[len(candidatos.index),:] = 'Lautaro','','Juan Ignacio Benítez','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Ignacio_Benítez'
            candidatos.loc[len(candidatos.index),:] = 'Los Ángeles','','Venancio Escanilla','','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Venancio_Escanilla'
            
# Don Rafael Bilbao (Huasco).
# Juan Buenaventura Marín Recabarren (Coquimbo).
# don Julián Navarro (Elqui)". #suplente: jose antonio perez cotapos
# José Miguel Infante (Petorca)6.
# Don Martín Orjera (La Ligua).
# Melchor de Santiago Concha (Los Andes).
# Don Manuel Sotomayor (Aconcagua).
# José Antonio Villar Fontecilla (Aconcagua).
# Don Manuel Echeverría (Quillota),
# José Gregorio Menescs (Casablanca).
# Don Santiago Muñoz de Bezanilla (Casablanca).
# Don Ángel Arguelles (Santiago).
# Don Enrique Campino (Santiago).
# Diego Antonio Elizondo (Santiago) # reemplazante francisco valdivieso vargas
# Don Bruno Larraín (Santiago).
# Blas de Reyes (Santiago).
# Don Miguel de Ureta (Melipilla).
# Don José Antonio Valdés Huidobro (Rancagua).
# Don Juan Albano Pereira (Colchagua).
# Don José Tomás Argomedo González (Colchagua).
# Melchor José Ramos (Colchagua).
# Don Antonio del Castillo (CuricÓ).
# Francisco de Borja Orihuela (Curicó),
# José Francisco Gana (Talca).
# Ignacio Molina (Linares).
# Don Pedro Femando Urízar (Linares).
# Don Manuel de Araoz (Cauquenes).
# Juan Antonio González Palma (Itata).
# Don Fernando Antonio Elizalde (San Carlos).
# Juan José Gutiérrez Palacios (Chillan).
# Pedro Nolasco Mena (Chillan) #renuncio, sumiendo como titilar agustin vial santelices
# Don Diego Antonio Barros (Coelemu).
# Pbro. don Juan Ignacio Benítez (Lautaro)'1, suplente: bernardo caceres
# Don Manuel Novoa (Concepción).
# Miguel Collao (Los Angeles).
# Agustín López (Los Angeles) #suplente: venancio escanilla
# Don Manuel José Gandarillas (Valdivia) #no se incorporó

# Don Juan Cortés (Chiloé).

# Manuel Renjifo (Chiloé).







            
    #no considera como duplicados los agregados para corregir 
    candidatos = candidatos.drop_duplicates(subset=['Candidatos'], keep="last")
    
    candidatos.loc[candidatos['Candidatos'].str.contains('|'.join(propietarios)), 'Electos'] = '*'
    
    return candidatos, reemplazados, reemplazantes, presuntivos, partidos