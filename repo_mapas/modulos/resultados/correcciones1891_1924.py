#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from modulos.pactos import pactos_electorales, siglas_partidos

import pandas as pd
pd.options.mode.chained_assignment = None

from pathlib import Path
import re
from operator import itemgetter
from ast import literal_eval

def correcciones1891_1924(candidatos, eleccion, rep):
    candidatos.loc[candidatos['Partido'] == 'Independiente', 'Partido'] = 'Candidatura Independiente'
    
    reemplazados = {0:['^$'], 1:['^$']}[rep]
    reemplazantes = {0:['^$'], 1:['^$']}[rep]
    presuntivos = {0:['^$'], 1:['^$']}[rep]
    partidos = {'^$': {0:['^$'], 1:['^$']}[rep]}
    
    if eleccion == 1924:
        presuntivos = {0:['Montané Urrejola', 'Germán Ignacio Riesco Errázuriz', 'Eduardo Errázuriz Larraín', 'Olavarría Bravo'], 1:['^$']}[rep]

        partidos = {'Partido Conservador': {0:['Eduardo Errázuriz Larraín'], 1:['^$']}[rep],
                    'Partido Liberal': {0:['Olavarría Bravo'], 1:['^$']}[rep],
                    'Partido Liberal Democrático': {0:['Palacios Baeza'], 1:['^$']}[rep]
                    }

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Solar Urrutia')):
            candidatos.loc[len(candidatos.index),:] = 'Parral','','Domingo Antonio Solar Urrutia','Partido Liberal','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Domingo_Antonio_Solar_Urrutia'
        
    if eleccion == 1921:
        reemplazados = {0:['Silva Cortés', ], 1:['^$']}[rep]
        reemplazantes = {0:['Tizzoni Lucciano'], 1:['^$']}[rep]
        presuntivos = {0:['Eduardo Opaso Letelier'], 1:['^$']}[rep]
        
        partidos = {'Partido Liberal': {0:['Garcés Gana'], 1:['^$']}[rep]
                    }                
        
        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Hormann Soruco')):
            candidatos.loc[len(candidatos.index),:] = 'Santiago','','Jorge Hörmann Soruco','Partido Nacional','','','*','*',''        
            candidatos.loc[len(candidatos.index),:] = 'Santiago','','Paulo Marín Pinuer','Partido Nacional','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Paulo_Marín_Pinuer'
        
    if eleccion == 1918:
        reemplazados = {0:['Vial Solar', 'Acuña Valdivia'], 1:['^$']}[rep]
        reemplazantes = {0:['Javier Bustamante', 'Paredes Pacheco'], 1:['^$']}[rep]
        presuntivos = {0:['Juliet Ossa', 'Balmaceda Saavedra'], 1:['^$']}[rep]
        
        # falta la militancia de j.javier bustamante
        partidos = {'Partido Liberal': {0:['Somarriva Undurraga'], 1:['^$']}[rep],
                    'Partido Liberal Doctrinario': {0:['Cubillos Pareja'], 1:['^$']}[rep],
                    'Partido Democrático': {0:['Gutiérrez Vidal'], 1:['^$']}[rep]
                    }
                
        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Díaz Garcés')):
            candidatos.loc[len(candidatos.index),:] = 'Laja','','Joaquín del Tránsito Díaz Garcés','Partido Nacional','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Joaquín_Del_Tránsito_Díaz_Garcés'
                
    if eleccion == 1915:
        reemplazados = {0:['Cortés Cabezas','Eyzaguirre Rouse', 'Pozo Urzúa', 'Bahamonde Hoppe'], 1:['^$']}[rep]
        reemplazantes = {0:['Silva Endeiza', 'Ibáñez Ibáñez', 'Hederra Concha', 'Coveña Donoso'], 1:['^$']}[rep]
        presuntivos = {0:[ 'Barrios Castellón'], 1:['^$']}[rep]


        #falta la militancia de barrios castellon (ovalle), hederra concha
        partidos = {'Partido Nacional': {0:['Prat Carvajal', 'Irarrázaval Smith', 'Letelier Espínola', 'Pozo Urzúa'], 1:['^$']}[rep],
                    'Partido Radical': {0:['Rivera Alcayaga', 'Videla Cortés', 'Vital Sánchez', 'Coveña Donoso', 'Fernández Íñiguez', 'Anguita Anguita'], 1:['^$']}[rep], 
                    'Partido Conservador': {0:['Urrejola Mulgrew', 'Subercaseaux Pérez'], 1:['^$']}[rep],
                    'Partido Liberal Doctrinario': {0:['Iñiguez Larraín'], 1:['^$']}[rep],
                    'Partido Liberal': {0:['Matte Larraín', 'Orrego Barros'], 1:['^$']}[rep],
                    'Partido Democrático': {0:['Cárdenas Avendaño'], 1:['^$']}[rep]
                    }
        
        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Concha Ortiz')):
            candidatos.loc[len(candidatos.index),:] = 'Temuco','','Malaquías Concha Ortiz','Partido Democrático','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Malaquías_Concha_Ortiz'
        
    if eleccion == 1912:
        reemplazados = {0:['Maira González', 'Gallardo González'], 1:['^$']}[rep]
        reemplazantes = {0:['Castellón Larenas', 'Barrios Ugalde'], 1:['^$']}[rep]
        presuntivos = {0:['Contreras Sotomayor', 'Ismael Vicuña Subercaseaux', 'Luis Aurelio Pinochet', 'Rivera Ojeda', 'Möhr Pérez'], 1:['^$']}[rep]

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Concha Ortiz')):
            candidatos.loc[len(candidatos.index),:] = 'Concepción','','Malaquías Concha Ortiz','Partido Democrático','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Malaquías_Concha_Ortiz'
        
    if eleccion == 1909:
        reemplazados = {0:['Suárez Mujica', 'Edwards Mac-Clure', 'Rivas Ramírez', 'Foster Recabarren', 'Pereira Gandarillas', 'Figueroa Larraín', 'Rivera Ojeda', 'Irarrázaval Zañartu', 'Manterola de la Fuente'], 1:['^$']}[rep]
        reemplazantes = {0:['Gandarillas Matta', 'Larraín Valdés','Gutiérrez Martínez', 'Foster Recabarren', 'Silva Cortés', 'Sánchez García de la Huerta', 'Pinto Cruz', 'Smitmans Rothamel', 'Rivera González'], 1:['^$']}[rep]
        presuntivos = {0:['León Silva', 'Juan de Dios Morandé Vicuña'], 1:['^$']}[rep]

        # faltan varias militancias
        partidos = {'Partido Conservador': {0:['Eguiguren Valero', 'Enrique Morandé Vicuña', 'Urzúa Rojas'], 1:['^$']}[rep],
                    'Partido Liberal': {0:['Irarrázaval Zañartu'], 1:['^$']}[rep],
                    }
        
        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Concha Ortiz')):
            candidatos.loc[len(candidatos.index),:] = 'Concepción','','Malaquías Concha Ortiz','Partido Democrático','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Malaquías_Concha_Ortiz'

    if eleccion == 1906:
        reemplazados = {0:['Cruz Díaz', 'Pinto Agüero', 'Sanfuentes Moreno', 'Valenzuela Larenas'], 1:['^$']}[rep]
        reemplazantes = {0:['Agustín Edwards Mac-Clure', 'García de la Huerta Izquierdo', 'Balmaceda Toro', 'Figueroa Larraín'], 1:['^$']}[rep]
        presuntivos = {0:['Recabarren Serrano'], 1:['^$']}[rep]

        # faltan varias militancias
        partidos = {'Partido Conservador': {0:['Concha Subercaseaux'], 1:['^$']}[rep]
                    }

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Concha Ortiz')):
            candidatos.loc[len(candidatos.index),:] = 'Concepción','','Malaquías Concha Ortiz','Partido Democrático','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Malaquías_Concha_Ortiz'

    if eleccion == 1903:
        reemplazados = {0:['Figueroa Larraín', 'Errázuriz Echenique', 'Pinto Izarra', 'Ríos González', 'Vásquez Guarda'], 1:['^$']}[rep]
        reemplazantes = {0:['Walker Martínez', 'Francisco Echenique Gandarillas', 'Yáñez Ponce de León', 'Zañartu Prieto', 'Huneeus Gana'], 1:['^$']}[rep]
        presuntivos = {0:['Valdés Vergara', 'Aldunate Bascuñán', 'Larraín Alcalde', 'Armanet Vergara', 'Germán Munita', 'Leiva Rodríguez', 'Gacitúa Brieba', 'José Miguel Echenique Gandarillas'], 1:['^$']}[rep]

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Concha Ortiz')):
            candidatos.loc[len(candidatos.index),:] = 'Concepción','','Malaquías Concha Ortiz','Partido Democrático','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Malaquías_Concha_Ortiz'
        
    if eleccion == 1900:
        reemplazados = {0:['Bello Codesido', 'Mac Clure Ossandón', 'Walker Martínez', 'del Río Villalobos'], 1:['^$']}[rep]
        reemplazantes = {0:['Vicuña Subercaseaux', 'Bascuñán Santa María', 'Landa Zárate', 'Aldunate Bascuñán'], 1:['^$']}[rep]
        presuntivos = {0:['Pleiteado Cevallos', 'Blanlot Holley', 'Manuel Veillon', 'Hevia Riquelme', 'Echaurren Valero', 'Burgos Figueroa', 'Corbalán Melgarejo'], 1:['^$']}[rep]
        
        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Concha Ortiz')):
            candidatos.loc[len(candidatos.index),:] = 'Concepción','','Malaquías Concha Ortiz','Partido Democrático','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Malaquías_Concha_Ortiz'
        
    if eleccion == 1897:
        reemplazados = {0:['Salinas González', 'Bañados Espinosa'], 1:['^$']}[rep]
        reemplazantes = {0:['Robinet Lambarri', 'Pérez Montt'], 1:['^$']}[rep]
        presuntivos = {0:['Alemany Sánchez', 'Sánchez Massenlli', 'Alberto Sanfuentes Moreno', 'Concha Ortiz'], 1:['^$']}[rep]

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Herboso España')):
            candidatos.loc[len(candidatos.index),:] = 'Rancagua','','Francisco Herboso España','Partido Liberal Democrático','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Francisco_Herboso_España'
            candidatos.loc[len(candidatos.index),:] = 'Concepción','','Malaquías Concha Ortiz','Partido Democrático','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Malaquías_Concha_Ortiz'        

    if eleccion == 1894:
        reemplazados = {0:['Walker Martínez', 'Mathieu Andrews'], 1:['^$']}[rep]
        reemplazantes = {0:['Aldunate Bascuñán', 'Fredes Ortiz'], 1:['^$']}[rep]
        presuntivos = {0:['^$'], 1:['^$']}[rep]
        
        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Herboso España')):
            candidatos.loc[len(candidatos.index),:] = 'Rancagua','','Francisco Herboso España','Partido Liberal Democrático','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Francisco_Herboso_España'
            candidatos.loc[len(candidatos.index),:] = 'Yungay','','Juan Enrique Tocornal Doursther','Partido Conservador','','','*','*',''
        
    if eleccion == 1891:
        reemplazados = {0:['^$'], 1:['^$']}[rep]
        reemplazantes = {0:['^$'], 1:['^$']}[rep]
        presuntivos = {0:['Letelier Silva'], 1:['^$']}[rep]

        partidos = {'Partido Radical': {0:['Silva Whittaker', 'Rodríguez Rozas', 'Robinet Lambarri', 'Tocornal Tocornal', 'González Julio', 'Urrutia Rozas', 'Pleiteado Cevallos', 'Reyes Basso'], 1:['^$']}[rep],
                    'Partido Liberal': {0:['Correa Sanfuentes', 'Valdés Valdés', 'Jordán Tocornal', 'Federico Errázuriz Echaurren', 'González Ibieta', 'Alberto Montt Montt', 'Serrano Vásquez', 'Zegers García-Huidobro', 'Videla Correas', 'Vásquez Larenas'], 1:['^$']}[rep],
                    'Partido Liberal Democrático': {0:['Zavala Varas'], 1:['^$']}[rep],
                    'Partido Nacional': {0:['Pedro Montt Montt'], 1:['^$']}[rep],
                    'Partido Conservador': {0:['Edwards Garriga', 'Matte Pérez', 'Larraín Alcalde', 'González Errázuriz', 'Lisboa Huerta', 'Joaquín Walker Martínez'],  1:['^$']}[rep]
                    }
        
        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Tocornal Doursther')):
            candidatos.loc[len(candidatos.index),:] = 'Yungay','','Juan Enrique Tocornal Doursther','Partido Conservador','','','*','*',''
        
    candidatos = candidatos.drop_duplicates(subset=['Candidatos'], keep="last")
    
    return candidatos, reemplazados, reemplazantes, presuntivos, partidos

