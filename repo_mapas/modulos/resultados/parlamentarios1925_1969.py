#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
pd.options.mode.chained_assignment = None

from pathlib import Path
import re
from operator import itemgetter
from ast import literal_eval

from pactos import pactos_electorales, siglas_partidos
from resultados_miscelaneo import nombres_formato

def parlamentarios1925_1969(path_datos, candidatos, eleccion, rep, siglas=None):
    """
    Corrección de datos electorales en el período 1925-1969, a partir de información
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
    reemplazados, reemplazantes = [], []

    if rep == 1 and eleccion != 1932 and not bool(sorted(path_datos.glob('*Circunscripcion*_electos.csv'))): 
        path_datos_prev = path_datos.parents[0]/str(eleccion-(4+(eleccion==1937)))
        datos_filenames = sorted(path_datos_prev.glob('*Circunscripcion*_electos.csv'))
        electos_prev = pd.read_csv(datos_filenames[0]) 
        electos_prev['Candidatos'] = electos_prev['Candidatos'].apply(lambda x : literal_eval(str(x))).apply(' '.join)
        
        electos_prev = electos_prev[electos_prev['Circunscripción'].isin([2,4,6,8,10] if (eleccion -1937)%8 == 0 else [1,3,5,7,9])]
        
        candidatos = pd.concat([candidatos, electos_prev], axis=0)
        candidatos = candidatos[~candidatos['Candidatos'].str.lower().duplicated(keep="last")]

        candidatos = candidatos[candidatos['Electos_comp'] == '*']  
        candidatos['Electos'] = '*'
        candidatos = candidatos.fillna('')

    ## cambios en candidatos
    (candidatos, reemplazados, reemplazantes, militancia) = correcciones1925_1969(candidatos, eleccion, rep)

    if reemplazados:
        candidatos.loc[candidatos['Candidatos'].str.contains('|'.join(reemplazados)), 'Electos_comp'] = None

    if reemplazantes: 
        candidatos.loc[candidatos['Candidatos'].str.contains('|'.join(reemplazantes)), 'Electos'] = None

    for partido, parlamentarios in militancia.items():        
        candidatos.loc[candidatos['Candidatos'].str.contains('|'.join(parlamentarios)), 'Partido'] = siglas[partido] if siglas else partido

    candidatos[subdivrow] = candidatos[subdivrow].astype(int)  

    #verificar si están todos los diputados
    if False:
        count = candidatos[candidatos['Electos'] == '*'].groupby(['Distrito']).agg({'Electos':'count'})    
        if eleccion >= 1969:
            count['escanos'] = [4,7,2,7,3,12,5,6,4,3,5,3,4,3,5,9,2,4,6,10,5,3,3,3,2,2,18,5,5]
        elif eleccion >= 1941:
            count['escanos'] = [4,7,2,7,3,12,5,6,4,3,5,3,4,3,5,9,2,4,6,10,5,3,3,3,1,18,5,5]
        elif eleccion == 1937:
            count['escanos'] = [4,7,2,7,3,12,5,6,4,3,5,3,4,3,5,9,2,6,4,9,8,3,3,1,18,5,5]
        elif eleccion == 1932:
            count['escanos'] = [4,7,2,7,3,12,4,6,4,3,4,2,4,3,5,7,4,6,4,9,8,3,3,1,18,5,5]
        elif eleccion == 1930:
            count['escanos'] = [5,6,2,7,5,11,18,5,4,6,4,5,4,4,6,5,4,3,4,4,6,7,4,4]
        elif eleccion == 1925:
            count['escanos'] = [4,6,2,7,5,11,18,5,4,6,4,5,4,4,6,5,4,3,4,4,6,7,4,4]            
        
        count['diff'] = count['escanos'] -count['Electos']
        
        print('TOTAL : ', count['escanos'].sum())
    
        print('DESAJUSTES')
        print(count[count['diff'] != 0])
        print(candidatos[candidatos['Distrito'].isin(count[count['diff'] != 0].index)][['Distrito','Candidatos']].sort_values(['Candidatos']).sort_values(['Distrito']))
    
        print('')
        
        print('REEMPLAZOS')        
        print(candidatos[(candidatos['Electos_comp'] == '*') & (candidatos['Electos'] != '*')]['Candidatos'])

    return candidatos

def correcciones1925_1969(candidatos, eleccion, rep):
    """
    Parameters
    ----------
    path_datos : TYPE
        DESCRIPTION.
    candidatos : TYPE
        DESCRIPTION.
    eleccion : TYPE
        DESCRIPTION.
    rep : TYPE
        DESCRIPTION.

    Returns
    -------
    candidatos : TYPE
        DESCRIPTION.
    reemplazados : TYPE
        DESCRIPTION.
    reemplazantes : TYPE
        DESCRIPTION.
    partidos : TYPE
        DESCRIPTION.

    """
    if eleccion == 1969:
        reemplazados = {0:['Pontigo Urrutia', 'Lacoste Navarro', 'Avendaño Ortúzar'], 1:['Isla Hevia']}[rep]
        reemplazantes = {0:['Altamirano Guerrero', 'Marín Socías', 'Diez Urzúa'], 1:['Moreno Rojas']}[rep]

        partidos = {'Partido Socialista': {0:['Sabat Gozalo'], 1:['^$']}[rep],
                    'Partido Social Demócrata': {0:['^$'], 1:['Luengo Escalona']}[rep],
                    'Partido Demócrata Cristiano': {0:['^$'], 1:['Jerez Horta']}[rep],
                    'Acción Popular Independiente': {0:['^$'], 1:['Tarud Siwady']}[rep],
                    'Unión Socialista Popular': {0:['^$'], 1:['Chadwick Valdés']}[rep]
                    }

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Juan Bautista Segundo Argandoña Cortéz')):        
            candidatos.loc[len(candidatos.index),:] = 2,'','Juan Bautista Segundo Argandoña Cortéz','Partido Demócrata Cristiano','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Bautista_Segundo_Argandoña_Cortéz'
            candidatos.loc[len(candidatos.index),:] = 71,'','Alvaro Erich Schnake Silva','Partido Socialista','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Alvaro_Erich_Schnake_Silva'

    elif eleccion == 1965:
        reemplazados = {0:['Muñoz Horz', 'Coñuepán Huenchual'], 1:['Corbalán González', 'García González']}[rep]
        reemplazantes = {0:['Montedónico Nápoli', 'Merino Jarpa'], 1:['Carrera Villavicencio', 'Baltra Cortés']}[rep]

        partidos = {'Partido Comunista': {0:['Melo Paéz'], 1:['^$']}[rep],
                    'Partido Democrático Nacional': {0:['González Maertens'], 1:['^$']}[rep],
                    'Partido Demócrata Cristiano': {0:['Lavandero Illanes'], 1:['^$']}[rep],
                    'Partido Socialista': {0:['^$'], 1:['Chadwick Valdés', 'Tarud Siwady']}[rep],
                    }

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Juan Bautista Segundo Argandoña Cortéz')):
            candidatos.loc[len(candidatos.index),:] = 2,'','Juan Bautista Segundo Argandoña Cortéz','Partido Demócrata Cristiano','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Bautista_Segundo_Argandoña_Cortéz'
        if (rep == 1) and not sum(candidatos['Candidatos'].str.contains('Carrera Villavicencio')): 
            candidatos.loc[max(candidatos.index)+1,:] = 5,'','María Elena Carrera Villavicencio','Partido Socialista','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/María_Elena_Carrera_Villavicencio'
            candidatos.loc[max(candidatos.index)+1,:] = 6,'','José Antonio Foncea Aedo','Partido Demócrata Cristiano','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Antonio_Foncea_Aedo'

    elif eleccion == 1961: 
        candidatos = candidatos[~candidatos['Candidatos'].str.contains('Jorge Wachholtz Araya')]
        
        reemplazados = {0:['Pinto Díaz', 'Naranjo Jara'], 1:['Tomic Romero']}[rep]
        reemplazantes = {0:['Monckeberg Barros', 'Naranjo Arias'], 1:['Prado Casas']}[rep]

        # la nacion, 7/3/61, p.1
        partidos = {'Partido Liberal': {0:['Klein Doerner'], 1:['^$']}[rep],
                    'Partido Socialista': {0:['^$'], 1:['Chelén Rojas', 'Palacios González']}[rep],
                    'Partido Demócrata Cristiano': {0:['^$'], 1:['Frei Montalva', 'Echavarri Elorza']}[rep],
                    'Partido Conservador Unido': {0:['^$'], 1:['Bulnes Sanfuentes', 'Vial Espantoso']}[rep],
                    'Candidatura Independiente': {0:['^$'], 1:['Tarud Siwady', 'Barrueto Reeve']}[rep]
                    }

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Ramón Augusto Silva Ulloa')):        
            candidatos.loc[len(candidatos.index),:] = 2,'','Juan Bautista Segundo Argandoña Cortéz','Partido Demócrata Cristiano','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Bautista_Segundo_Argandoña_Cortéz'
            candidatos.loc[len(candidatos.index),:] = 2,'','Ramón Augusto Silva Ulloa','Partido Socialista','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Ramón_Augusto_Silva_Ulloa'
            candidatos.loc[len(candidatos.index),:] = 6,'','Guillermo Rivera Bustos','Partido Liberal','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Guillermo_Rivera_Bustos' 
            candidatos.loc[len(candidatos.index),:] = 6,'','Alonso Zumaeta Faune','Partido Socialista','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Alonso_Zumaeta_Faune'
            candidatos.loc[len(candidatos.index),:] = 21,'','Juan Tuma Masso','Partido Democrático Nacional','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Tuma_Masso'        

    elif eleccion == 1957:
        candidatos.loc[candidatos['Partido'] == 'Partido Comunista de Chile', 'Partido'] = 'Partido del Trabajo'
        candidatos.loc[candidatos['Partido'] == 'Partido Demócrata Cristiano', 'Partido'] = 'Falange Nacional'
        candidatos.loc[candidatos['Partido'] == 'Partido Democrático del Pueblo', 'Partido'] = 'Partido Democrático'

        candidatos.loc[candidatos['Candidatos'].str.contains('Wachholtz Araya'), ['Candidatos','Partido','url']] = ['Francisco Alejandro Roberto Wachholtz Araya', 'Partido Radical', 'https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Francisco_Alejandro_Roberto_Wachholtz_Araya']

        reemplazados = {0:['Zepeda Barrios', 'Rojas Wolff', 'Mallet Simonetti'], 1:['Marín Balmaceda', 'Jorge Alessandri Rodríguez']}[rep]
        reemplazantes = {0:['Mercado Illanes', 'Edwards Orrego', 'Zumaeta Faune'], 1:['Zepeda Barrios', 'Wachholtz Araya']}[rep]

        # fuente : la nacion, 5/3/1957, p.2; y 10/3/1957, p.4
        partidos = {'Partido Nacional': {0:["Hurtado O'Ryan", 'Gormaz Molina', 'Lobos Arias', 'Widmer Ewertz', 'Valdés Solar', 'Lavandero Illanes', 'Raúl Aldunate Phillips', 'Momberg Roa'],
                                         1:['Pérez de Arce Plummer', 'Lavandero Eyzaguirre']}[rep], 
                    'Partido Liberal': {0:['^$'], 1:['Amunátegui Jordán']}[rep],
                    'Partido Socialista': {0:['Ahumada Trigo', 'Cademártori Invernizzi'], 1:['Ahumada Pacheco']}[rep],
                    'Partido Socialista Popular': {0:['^$'], 1:['Palacios González']}[rep], 
                    'Partido Democrático': {0:['Oyarzún Decouvieres', 'Martones Morales'], 1:['Martones Quezada']}[rep],
                    'Partido Conservador Unido': {0:['Serrano de Viale-Rigo'],
                                                  1:['Cerda Jaraquemada', 'Larraín Vial', 'Coloma Mellado', 'Bulnes Sanfuentes', 'Curti Cannobio']}[rep],
                    'Partido Conservador Social Cristiano': {0:['^$'], 1:['Vial Espantoso']}[rep], 
                    'Movimiento Republicano': {0:['^$'], 1:['Videla Ibáñez']}[rep],
                    'Partido Agrario Laborista': {0:['^$'], 1:['Tarud Siwady']}[rep],
                    'Candidatura Independiente': {0:['Meneses Dávila'], 1:['Jorge Alessandri Rodríguez']}[rep]
                    }
            
        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Ramón Augusto Silva Ulloa')):
            candidatos.loc[len(candidatos.index),:] = 2,'','Ramón Augusto Silva Ulloa','Partido Socialista Popular','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Ramón_Augusto_Silva_Ulloa'
            candidatos.loc[len(candidatos.index),:] = 6,'','Alonso Zumaeta Faune','Partido Socialista','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Alonso_Zumaeta_Faune'
            candidatos.loc[len(candidatos.index),:] = 71,'','Luis Pareto González','Partido Agrario Laborista','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Luis_Pareto_González'        
        if (rep == 1) and not sum(candidatos['Candidatos'].str.contains('Barrueto Reeve')): 
            candidatos.loc[max(candidatos.index)+1,:] = 8,'','Edgardo Barrueto Reeve','Partido Agrario Laborista','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Edgardo_Barrueto_Reeve'

    elif eleccion == 1953:
        reemplazados = {0:['Zárate Andreu', 'Montero Soto', 'Pizarro Cabezas', 'Benaprés Lafourcade', 'Nazar Feres', 'Recabarren Valenzuela','Muñoz San Martín'],
                        1:['Cruz Toledo']}[rep]
        reemplazantes = {0:['Maurás Novella', 'Flores Álvarez', 'Corral Garrido', 'Pumarino Fuentes', 'Muñoz Horz', 'Gumucio Vives', 'Barja Blanco'],
                         1:['Quinteros Tricot']}[rep]

        #fuente : la nacion, 3/3/1953, pp.6 y 8
        partidos = {'Partido Conservador Social Cristiano': {0:['Palma Sanguinetti', 'Palma Gallardo'], 1:['^$']}[rep],
                    'Partido Conservador Tradicionalista': {0:['^$'], 1:['Cerda Jaraquemada', 'Bulnes Sanfuentes', 'Curti Cannobio']}[rep],
                    'Partido Socialista Popular': {0:['Naranjo Jara', 'Hernández Barrientos'], 1:['Martínez Martínez', 'Rodríguez Arenas']}[rep],
                    'Partido Radical': {0:['^$'], 1:['Figueroa Anguita']}[rep], 
                    'Movimiento Nacional Ibañista': {0:['Jerez Contreras', 'Acevedo Pavez'], 1:['Videla Ibáñez', 'Pérez de Arce Plummer']}[rep],
                    'Partido Laborista': {0:['Rivera González'], 1:['^$']}[rep],
                    'Partido Agrario Laborista': {0:['Muñoz San Martín'], 1:['Pedregal Artigas']}[rep],
                    'Partido Agrario': {0:['Lobos Arias', 'Echavarri Elorza'], 1:['^$']}[rep],
                    'Unión Nacional de Independientes': {0:['Ojeda Doren', 'Justiniano Préndez'], 1:['Ahumada Pacheco']}[rep],
                    'Movimiento Nacional del Pueblo': {0:['^$'], 1:['Lavandero Eyzaguirre']}[rep]
                    }

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Ramón Augusto Silva Ulloa')):
            candidatos.loc[len(candidatos.index),:] = 2,'','Ramón Augusto Silva Ulloa','Partido Socialista Popular','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Ramón_Augusto_Silva_Ulloa'        
            candidatos.loc[len(candidatos.index),:] = 17,'','Adán Puentes Gómez','Partido Democrático del Pueblo','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Adán_Puentes_Gómez'        
            candidatos.loc[len(candidatos.index),:] = 19,'','Jorge Rigo-Righi Caridi','Partido Agrario Laborista','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Jorge_Rigo_Righi_Caridi'        
            candidatos.loc[len(candidatos.index),:] = 21,'','Edgardo Barrueto Reeve','Partido Agrario Laborista','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Edgardo_Barrueto_Reeve'               
            candidatos.loc[len(candidatos.index),:] = 71,'','Eduardo Maass Jensen','Partido Socialista Popular','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Edgardo_Maass_Jensen'        

    elif eleccion == 1949: 
        candidatos = candidatos[~candidatos['Candidatos'].str.contains('Quinteros Tricot')]

        # Senador fallecido antes de empezar el segundo período, lo reemplaza Sergio Fernández Larraín
        candidatos.loc[candidatos['Candidatos'].str.contains('Cruchaga Tocornal'), ['Electos', 'Electos_comp']] = [None, None]
        
        candidatos.loc[candidatos['Partido'] == 'Partido Conservador', 'Partido'] = 'Partido Conservador Social Cristiano'
        candidatos.loc[candidatos['Partido'] == 'Partido Social Cristiano', 'Partido'] = 'Partido Conservador Social Cristiano'

        reemplazados = {0:['Souper Maturana', 'Bravo Santibáñez', 'Muñoz García', 'Maira Castellón', 'Cifuentes Sobarzo', 'Cárdenas Núñez', 'Concha Molina'],
                        1:['Reyes Basoalto', 'Arturo Alessandri Palma', 'Ibáñez del Campo', 'Moller Bordeu']}[rep]
        reemplazantes = {0:['Cruz Ponce', 'Noguera Prieto', 'Inés Leonor Enríquez Frodden', 'Puga Fisher', 'Puga Vega'],
                         1:['Tomic Romero', 'Arturo Matte Larraín', 'Cruz Toledo', 'Maira Castellón']}[rep]

        #fuente: la nación, 8/3/1949, pp.1-2; y https://es-academic.com/dic.nsf/eswiki/421251
        partidos = {'Partido Radical Democrático': {0:['Torres Galdames','Rivas Fernández','Arenas Aguiar', 'Mejías Concha', 'Moller Bordeu','Sepúlveda Rondanelli', 'Durán Neumann'], 1:['Figueroa Anguita']}[rep],
                    'Partido Radical': {0:['Barrientos Villalobos'], 1:['^$']}[rep],
                    'Partido Socialista Popular': {0:['Galleguillos Clett', 'Tapia Moore', 'Rodríguez Arenas', 'Olavarría Alarcón', 'Castro Palma'], 1:['González Rojas']}[rep],
                    'Partido Liberal': {0:['Pizarro Cabezas', 'Braun Page', 'Alfonso Campos Menéndez','Raúl Aldunate Phillips'], 1:['Opaso Cousiño', 'Amunátegui Jordán']}[rep],
                    'Partido Democrático del Pueblo': {0:['Martones Quezada'], 1:['^$']}[rep],
                    'Partido Agrario Laborista': {0:['Echavarri Elorza'], 1:['Ibáñez del Campo', 'Pedregal Artigas']}[rep],
                    'Falange Nacional':{0:['^$'], 1:['Frei Montalva', 'Tomic Romero']}[rep],  
                    'Partido Conservador Social Cristiano': {0:['^$'], 1:['Muñoz Cornejo', 'Eduardo Cruz Coke Lassabe']}[rep],
                    'Partido Conservador Tradicionalista': {0:['^$'], 1:['Cerda Jaraquemada', 'Rodríguez de la Sotta', 'Fernández Larraín', 'Pereira Larraín', 'Aldunate Errázuriz', 'Prieto Concha']}[rep]
                    }

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Edgardo Barrueto Reeve')):                        
            candidatos.loc[len(candidatos.index),:] = 21,'','Edgardo Barrueto Reeve','Partido Liberal Progresista','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Edgardo_Barrueto_Reeve'               
            candidatos.loc[len(candidatos.index),:] = 24,'','José Edesio García Setz','Partido Conservador Social Cristiano','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Edesio_García_Setz'        

    elif eleccion == 1945:
        if rep == 1: 
            candidatos = candidatos[~candidatos['Candidatos'].str.contains('Tomic Romero|Fernández Larraín|Maira Castellón')]
        
        candidatos.loc[candidatos['Partido'] == 'Partido Comunista de Chile', 'Partido'] = 'Partido Progresista Nacional'
        candidatos.loc[candidatos['Partido'] == 'Partido Agrario Laborista', 'Partido'] = 'Partido Agrario'

        reemplazados = {0:['Cisternas Ortíz', 'Escala Garnham', 'Carrasco Rábago', 'Cabezón Díaz', 'Madrid Osorio', 'Cifuentes Latham', 'Chesta Pastoureaud', 'del Canto Medán',
                        'Araya Zuleta', 'Echeverría Moorhouse', 'Edwards Atherton', 'Osorio Navarrete'],
                        1:['González Videla', 'Echenique Zegers']}[rep]
        reemplazantes = {0:['Avilés Avilés', 'Durán Villarreal', 'Wiegand Frodden', 'Bedoya Hundesdoerffer', 'Moore Montero', 'Zañartu Urrutia', 'Sandoval Muñoz', 'Rogers Sotomayor'],
                         1:['Vásquez Galdames', 'Bulnes Correa']}[rep]

        #fuente : la nación, 5/3/1945, p.4
        partidos = {'Partido Socialista': {0:['Rossetti Colombino'], 1:['^$']}[rep],
                    'Partido Socialista Auténtico': {0:['^$'], 1:['Domínguez Domínguez', 'Marmaduke Grove Vallejo']}[rep],
                    'Partido Agrario': {0:['Echavarri Elorza'], 1:['^$']}[rep],
                    'Partido Conservador': {0:['Escala Garnham'], 1:['Cerda Jaraquemada']}[rep],
                    'Partido Progresista Nacional': {0:['Godoy Urrutia'], 1:['^$']}[rep], 
                    'Alianza Popular Libertadora': {0:['Coñuepán Huenchual'], 1:['^$']}[rep], 
                    'Partido Liberal Progresista': {0:['Bustos León'], 1:['^$']}[rep],
                    'Partido Liberal': {0:['^$'], 1:['Bulnes Correa']}[rep],
                    'Partido Radical': {0:['^$'], 1:['Bórquez Pérez']}[rep]
                    }

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Héctor Zañartu Urrutia')):
            candidatos.loc[len(candidatos.index),:] = 16,'','Héctor Zañartu Urrutia','Partido Conservador','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Héctor_Zañartu_Urrutia'
            candidatos.loc[len(candidatos.index),:] = 21,'','Braulio Sandoval Muñoz','Partido Agrario','','',None,'*',''            
            candidatos.loc[len(candidatos.index),:] = 25,'','Juan Rafael Del Canto Medán','Partido Liberal Democrático','','','*',None,'https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Rafael_Del_Canto_Medán'
            candidatos.loc[len(candidatos.index),:] = 71,'','Roberto Barros Torres','Partido Liberal','','','*',None,'https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Roberto_Barros_Torres'

        if (rep == 1) and not sum(candidatos['Candidatos'].str.contains('Vásquez Galdames')): 
            candidatos.loc[max(candidatos.index)+1,:] = 1,'','Angel Custodio Vásquez Galdames','Partido Radical','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Angel_Custodio_Vásquez_Galdames'

    elif eleccion == 1941: 
        candidatos = candidatos[~candidatos['Candidatos'].str.contains('Vásquez Galdames|Ballesteros Reyes')]                
        
        candidatos.loc[candidatos['Partido'] == 'Partido Comunista de Chile', 'Partido'] = 'Partido Progresista Nacional'

        reemplazados = {0:['Ollino Buzeta', 'Muñoz Ayling', 'Rosende Verdugo', 'Rossetti Colombino', 'Montecinos Matus', 'Labarca Moreno', 'Ernst Martínez', 'Castelblanco Agüero'],
                        1:['Hiriart Corvalán', 'Pairoa Trujillo', 'Barrueto Molinet']}[rep]
        reemplazantes = {0:['Ollino Buzeta', 'Baeza Herrera', 'Jara del Villar', 'Godoy Urrutia', 'Brito Salvo', 'Pinedo Goycochea', 'Campos Menéndez'],
                         1:['Guzmán Cortés', 'Arturo Alessandri Palma', 'Larraín García-Moreno']}[rep]

        #fuente : la nación, 4/3/1941, p.4
        partidos = {'Partido Liberal': {0:['Labarca Moreno', 'Urrutia Infante'], 1:['Opaso Letelier', 'Amunátegui Jordán']}[rep],
                    'Partido Agrario': {0:['Echavarri Elorza'], 1:['Larraín García-Moreno']}[rep],
                    'Vanguardia Popular Socialista': {0:['González Von Marées'], 1:['^$']}[rep],
                    'Falange Nacional': {0:['Ceardi Ferrer', 'Garretón Walker'], 1:['^$']}[rep],
                    'Partido Socialista': {0:['^$'], 1:['Domínguez Domínguez']}[rep],
                    'Partido Socialista de Trabajadores': {0:['Berman Berman'], 1:['^$']}[rep], 
                    'Partido Radical Socialista': {0:['Rossetti Colombino'], 1:['^$']}[rep],
                    'Partido Progresista Nacional': {0:['Zamora Rivera'], 1:['Lafertte Gaviño']}[rep], 
                    'Partido Demócrata': {0:['Fuentealba Troncoso'], 1:['^$']}[rep], 
                    'Alianza Popular Libertadora': {0:['Bustos León'], 1:['^$']}[rep],
                    'Partido Conservador': {0:['^$'], 1:['Cruz Concha']}[rep]
                    }

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('César Godoy Urrutia')):
            candidatos.loc[len(candidatos.index),:] = 24,'','Alfonso Campos Menéndez','Partido Liberal','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Alfonso_Campos_Menéndez'            
            candidatos.loc[len(candidatos.index),:] = 25,'','Juan Rafael del Canto Medán','Partido Liberal Democrático','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Rafael_Del_Canto_Medán'
            candidatos.loc[len(candidatos.index),:] = 71,'','César Godoy Urrutia','Partido Progresista Nacional','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/César_Godoy_Urrutia'
                    
        if (rep == 1) and not sum(candidatos['Candidatos'].str.contains('Ortega Mason')): 
            candidatos.loc[max(candidatos.index)+1,:] = 8,'','Rudecindo Ortega Mason','Partido Radical','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Rudecindo_Ortega_Mason'
                                               
    elif eleccion == 1937:  
        candidatos = candidatos[~candidatos['Candidatos'].str.contains('Vásquez Galdames|Ballesteros Reyes|Guzmán Cortés')]
                
        candidatos.loc[candidatos['Partido'] == 'Partido Comunista de Chile', 'Partido'] = 'Partido Nacional Democrático'
        if rep == 0:
            candidatos.loc[candidatos['Partido'] == 'Partido Democrático', 'Partido'] = 'Partido Demócrata'
            candidatos.loc[candidatos['Candidatos'].str.contains('Latcham Alfaro'), 'Distrito'] = 71
            candidatos.loc[candidatos['Candidatos'].str.contains('Baeza Herrera'), ['Distrito','Partido']] = [72,'Partido Socialista']
            
        reemplazados = {0:['Puga Fisher',
                           'Alfonso Barrios', 'Martínez Martínez', 'Ortega Mason', 'Melo Hermosilla', 'Cifuentes Solar', 'González Videla', 'Allende Gossens', 'Merino Reyes', 'Álvarez Suárez', 'Pezoa Estrada', 'Luna Verdugo'],
                        1:['Schnake Vergara', 'Gatica Silva', 'Santa María Cerveró', 'Pradenas Muñoz', 'Meza Rivera', 'Sáenz Cerda']}[rep]
        reemplazantes = {0:['Puga Fisher',
                            'Alfonso Muñoz', 'Olivares Faúndez', 'López Urbina', 'Holzapfel Álvarez', 'Valck Vega', 'Ruiz Mondaca', 'Pinto Riquelme', 'Valdebenito García', 'Rosales Gutiérrez', 'Masson Villarroel', 'Alarcón del Canto', 'Freeman Caris'],
                         1:['Martínez Martínez', 'Méndez Arancibia', 'Cruzat Ortega', 'Venegas Sepúlveda', 'Silva Sepúlveda', 'Ortega Mason']}[rep]

        # fuente: la nación, 8/3/1937. p.21
        partidos = {'Partido Conservador': {0:['Ruiz Correa'], 1:['^$']}[rep],
                    'Partido Radical': {0:['Masson Villarroel', 'San Martín Fuentes', 'Morales Beltramí'], 1:['Bórquez Pérez']}[rep],
                    'Partido Nacional Democrático': {0:['Chamudes Reitich', 'Zapata Díaz'], 1:['^$']}[rep],
                    'Partido Socialista': {0:['Verdugo Espinoza', 'Berman', 'Merino Reyes', 'Barrenechea Pino'], 1:['^$']}[rep],
                    'Partido Liberal': {0:['del Pino Pereira', 'Madrid Arellano', 'Urrutia Ibañez'], 1:['Santa María Cerveró', 'Opaso Letelier', 'Haverbeck Richter']}[rep],
                    'Partido Agrario': {0:['Echavarri Elorza'], 1:['^$']}[rep],
                    'Movimiento Nacional Socialista': {0:['Vargas Molinare', 'González von Marées'], 1:['^$']}[rep],
                    'Partido Demócrata': {0:['Opaso Letelier'], 1:['^$']}[rep],
                    'Partido Democrático': {0:['Muñoz Moyano', 'Silva Pinto', 'Luna Verdugo', 'Francisco Antonio Lobos'], 1:['^$']}[rep],
                    'Candidatura Independiente': {0:['Arellano Figueroa', 'Guerra Guerra', 'Labbé Labbé'], 1:['^$']}[rep]
                    }

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('del Canto Medán')):
            candidatos.loc[len(candidatos.index),:] = 71,'','Gerardo López Urbina','Partido Socialista','','',None,'*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Gerardo_López_Urbina'
            candidatos.loc[len(candidatos.index),:] = 21,'','Rudecindo Ortega Mason','Partido Radical','','','*',None,'https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Rudecindo_Ortega_Mason'
            candidatos.loc[len(candidatos.index),:] = 24,'','Juan Rafael del Canto Medán','Partido Liberal','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Rafael_Del_Canto_Medán'
        
        if (rep == 1) and not sum(candidatos['Candidatos'].str.contains('Ortega Mason')):
            candidatos.loc[len(candidatos.index),:] = 2,'','José Manuel Ríos Arias','Partido Liberal','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Manuel_Ríos_Arias'
            candidatos.loc[len(candidatos.index),:] = 3,'','Enrique Bravo Ortiz','Partido Liberal','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Enrique_Bravo_Ortiz'
            candidatos.loc[len(candidatos.index),:] = 4,'','Máximo Venegas Sepúlveda','Partido Democrático','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Máximo_Venegas_Sepúlveda'
            candidatos.loc[len(candidatos.index),:] = 6,'','Matías Silva Sepúlveda','Partido Liberal','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Matías_Silva_Sepúlveda'
            candidatos.loc[len(candidatos.index),:] = 8,'','Rudecindo Ortega Mason','Partido Radical','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Rudecindo_Ortega_Mason'

    elif eleccion == 1932:
        candidatos = candidatos[~candidatos['Candidatos'].str.contains('Alfredo Rosende')]        
        
        if rep == 0:
            candidatos.loc[candidatos['Distrito'] == 1, 'Partido'] = 'Partido Radical Socialista' 
            candidatos.loc[candidatos['Candidatos'].str.contains('Chaparro Ruminot'), ['Distrito','Partido']] = [25, 'Partido Regionalista de Magallanes']                
        
        reemplazados = {0:['Grossert', 'Pinochet Alvis', 'Durán Morales', 'Mardones Guerrero', 'Gómez Pérez', 'González Quiroga',
                           'Bustamante Cordero', 'Serani Burgos', 'Acuña Robert', 'Becker Valdevellano', 'Álvarez Suárez', 'Prieto Concha', 'Elgueta González'],
                        1:['Núñez Morgado', 'Marambio Montt', 'Ugalde Naranjo', 'Matte Hurtado', 'Dagnino Olivieri', 'Gutiérrez Vidal']}[rep]
        reemplazantes = {0:['Grossert', 'Pinochet Alvis', 'Durán Morales', 'Mardones Guerrero', 'Gómez Pérez', 'González Quiroga',
                            'Raúl Cáceres', 'Freeman Caris',  'Döll Rojas', 'Sandoval Muñoz', 'Lyon Otaegui'],
                         1:['Alessandri Rodríguez', 'Ríos Arias', 'Ureta Echazarreta', 'Marmaduke Grove Vallejo', 'Aldunate Errázuriz', 'Sáenz Cerda']}[rep]

        # fuente: https://es-academic.com/dic.nsf/eswiki/421246    
        #falta un segundo liberal doctrinario            
        partidos = {'Partido Conservador': {0:['Pereira Lyon', 'Pérez Gacitúa', 'Aburto Oróstegui', 'Cañas Flores'], 1:['^$']}[rep],
                    'Partido Social Republicano': {0:['Carrasco Rábago'], 1:['Hidalgo Plaza']}[rep], 
                    'Nueva Acción Pública': {0:['Verdugo Espinoza', 'Martínez Martínez'], 1:['Matte Hurtado']}[rep], 
                    'Partido Radical': {0:['Acuña Robert', 'Lyon Otaegui'], 1:['Bórquez Pérez']}[rep], 
                    'Asociación Gremial de Empleados de Chile': {0:['Aguirre Pinto'], 1:['^$']}[rep], 
                    'Partido Democrático Socialista': {0:['Ferrada Riquelme'], 1:['^$']}[rep],
                    'Partido Socialista Unido': {0:['Zapata Díaz'], 1:['^$']}[rep],
                    'Partido Democrático': {0:['Casanova Ojeda', 'Escobar Delgado', 'González Quiroga', 'Vaillant'], 1:['^$']}[rep],
                    'Partido Demócrata': {0:['Retamales Leiva', 'Bustos Valenzuela', 'Chanks Camus', 'Zuñiga Dueñas', 'Gutiérrez Romero', 'Bosch Forgas'], 1:['Concha Stuardo', 'Morales Vivanco', 'Rozas Lopetegui']}[rep],
                    'Partido Liberal Unido': {0:['Zepeda Barrios', 'Rivera Baeza', 'Murillo Gaete', 'Dussaillant Louandre', 'Becerra Mera'], 1:['Santa María Cerveró', 'Opaso Letelier']}[rep],
                    'Partido Liberal Doctrinario': {0:['Amunátegui Jordán'], 1:['^$']}[rep],
                    'Partido Radical Socialista': {0:['^$'], 1:['Azócar Álvarez']}[rep],
                    'Candidatura Independiente': {0:['Vega Díaz', 'Escobar Díaz'], 1:['^$']}[rep]
                    }
            
        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('del Canto Medán')):
            candidatos.loc[len(candidatos.index),:] = 21,'','Rudecindo Ortega Mason','Partido Radical','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Rudecindo_Ortega_Mason'
            candidatos.loc[len(candidatos.index),:] = 24,'','Juan Rafael del Canto Medán','Partido Liberal Democrático','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Rafael_Del_Canto_Medán'
        
        if (rep == 1) and not sum(candidatos['Candidatos'].str.contains('Hugo Grove Vallejo')):
            candidatos.loc[len(candidatos.index),:] = 3,'','Hugo Grove Vallejo','Nueva Acción Pública','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Hugo_Grove_Vallejo'

    #no considera como duplicados los agregados para corregir 
    candidatos = candidatos.drop_duplicates(subset=['Candidatos'], keep="last")

    return candidatos, reemplazados, reemplazantes, partidos


            
                

            
            
            
            
        
                
            
    # elif eleccion == 1930:
    #     #elecciones complementarias
    #     reemplazados = ['Puelma Laval', 'Tamayo Torres', 'Ríos Arias', 'Wilson Hernández', 'Lillo Pacheco', 'Gutiérrez Reveco']
    #     reemplazantes = ['Elguín Morales', 'Ruiz Tagle Solar', 'Acuña Robert', 'Errázuriz Larraín', 'de Ferari Valdés', 'Barros Hurtado']

    #     #correcciones
    #     candidatos.loc[candidatos['Partido'].str.contains('Partido Democrático'), 'Partido'] = 'Partido Demócrata'
    #     candidatos.loc[candidatos['Partido'] == 'Partido Liberal', 'Partido'] = 'Partido Liberal Unido'
        
    #     candidatos.loc[candidatos['Candidatos'].str.contains('Gallo Sapiaín'), 'Partido'] = 'Partido Radical'
    #     candidatos.loc[candidatos['Candidatos'].str.contains('Elguín Morales'), 'Partido'] = 'Partido Radical'
    #     # de la Cuadra, Poisson PLU
    #     # munoz moyano democrata
    #     candidatos.loc[candidatos['Candidatos'].str.contains('de la Jara Zúniga'), 'Partido'] = 'Partido Liberal Unido'
    #     candidatos.loc[candidatos['Candidatos'].str.contains('Alegría Molina'), 'Partido'] = 'Confederación Republicana de Acción Cívica de Obreros y Empleados'        
    #     candidatos.loc[candidatos['Candidatos'].str.contains('Quevedo Vega'), 'Partido'] = 'Partido Demócrata'
        
    #     if not sum(candidatos['Candidatos'].str.contains('del Canto Medán')):
    #         candidatos.loc[len(candidatos.index),:] = 14,'','Juan Ernesto Rojas del Campo','Partido Radical','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Ernesto_Rojas_del_Campo'
    #         candidatos.loc[len(candidatos.index),:] = 20,'','Heriberto Arnechino Olate','Partido Demócrata','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Heriberto_Arnechino_Olate'
    #         candidatos.loc[len(candidatos.index),:] = 21,'','Rudecindo Ortega Mason','Partido Radical','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Rudecindo_Ortega_Mason'
    #         candidatos.loc[len(candidatos.index),:] = 24,'','Juan Rafael del Canto Medán','Partido Liberal Democrático','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Rafael_Del_Canto_Medán'

    # elif eleccion == 1925:
    #     #elecciones complementarias
    #     reemplazados = ['Troncoso Puga', 'Rivas Vicuña', 'Marín Troncoso', 'Guzmán Cortés', 'Donoso Henríquez']
    #     reemplazantes = ['Zañartu Urrutia', 'Reyes del Río', 'Vicuña Zorrilla', 'Marino Meléndez', 'Gabriel Letelier Elgart']

    #     # diputados presuntivos
    #     candidatos.loc[candidatos['Candidatos'].str.contains('Cuevas Contreras'), ['Electos','Electos_comp']] = [None, None]
    #     candidatos.loc[candidatos['Candidatos'].str.contains('Fuenzalida Cerda'), ['Electos','Electos_comp']] = [None, None]

    #     #correcciones
    #     #fuente: la nación, 24/11/1924, p.5
    #     candidatos.loc[candidatos['Partido'].str.contains('Partido Democrático'), 'Partido'] = 'Partido Demócrata'
    #     candidatos.loc[candidatos['Candidatos'].str.contains('de la Cuadra Poisson'), 'Partido'] = 'Partido Liberal Democrático'
    #     candidatos.loc[candidatos['Candidatos'].str.contains('Reyes Díaz'), 'Partido'] = 'Partido Comunista'
    #     candidatos.loc[candidatos['Candidatos'].str.contains('Vicuña Aguirre'), 'Partido'] = 'Partido Liberal Democrático'
    #     candidatos.loc[candidatos['Candidatos'].str.contains('Vicuña Zorrilla'), 'Partido'] = 'Partido Conservador'
    #     candidatos.loc[candidatos['Candidatos'].str.contains('Acuña Robert'), 'Partido'] = 'Partido Radical'
    #     candidatos.loc[candidatos['Candidatos'].str.contains('Ramírez Frías'), 'Partido'] = 'Partido Liberal'
    #     candidatos.loc[candidatos['Candidatos'].str.contains('Palacios Wilson'), 'Partido'] = 'Partido Liberal'
    #     candidatos.loc[candidatos['Candidatos'].str.contains('Troncoso Puga'), 'Partido'] = 'Partido Radical'
    #     candidatos.loc[candidatos['Candidatos'].str.contains('Bart Herrera'), 'Partido'] = 'Partido Comunista'
    #     candidatos.loc[candidatos['Candidatos'].str.contains('Alberto Collao'), 'Partido'] = 'Partido Liberal'
    #     candidatos.loc[candidatos['Candidatos'].str.contains('Barra Woll'), 'Partido'] = 'Partido Comunista'
    #     candidatos.loc[candidatos['Candidatos'].str.contains('de la Jara Zúniga'), 'Partido'] = 'Partido Liberal Democrático'
    #     candidatos.loc[candidatos['Candidatos'].str.contains('Rudloff Schmidt'), 'Partido'] = 'Partido Liberal'
    #     candidatos.loc[candidatos['Candidatos'].str.contains('Quevedo Vega'), 'Partido'] = 'Partido Comunista'

    #     candidatos.loc[candidatos['Candidatos'].str.contains('Manuel J. Navarrete'), 'Candidatos'] = 'Manuel Navarrete'
        
    #     if not sum(candidatos['Candidatos'].str.contains('del Canto Medán')):
    #         candidatos.loc[len(candidatos.index),:] = 14,'','Domingo Antonio del Solar Urrutia','Partido Liberal','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Domingo_Antonio_Solar_Urrutia'
    #         candidatos.loc[len(candidatos.index),:] = 21,'','Rudecindo Ortega Mason','Partido Radical','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Rudecindo_Ortega_Mason'
    #         candidatos.loc[len(candidatos.index),:] = 21,'','Juan Picasso Stagno','Partido Radical','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Picasso_Stagno'
    #         candidatos.loc[len(candidatos.index),:] = 24,'','Juan Rafael del Canto Medán','Partido Liberal Democrático','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Rafael_Del_Canto_Medán'
        
