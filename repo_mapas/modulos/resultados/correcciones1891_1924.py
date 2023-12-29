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
    ### queda revisar militancias entre 1891 y 1912, senadores del período
    
    candidatos.loc[candidatos['Partido'] == 'Independiente', 'Partido'] = 'Candidatura Independiente'
    
    reemplazados = {0:['^$'], 1:['^$']}[rep]
    reemplazantes = {0:['^$'], 1:['^$']}[rep]
    presuntivos = {0:['^$'], 1:['^$']}[rep]
    partidos = {'^$': {0:['^$'], 1:['^$']}[rep]}
    
    if eleccion == 1924:
        #fuente: la nacion, 2 y 4/marzo/1924 y 15/mayo/1924
        
        reemplazados = {0:['^$'], 1:['José Pedro Alessandri Palma']}[rep]
        reemplazantes = {0:['^$'], 1:['Juan Serrano Squella']}[rep]
        
        #en Linares, Onofre Lillo fue electo de forma presuntiva ?
        presuntivos = {0:['Montané Urrejola', 'Germán Ignacio Riesco Errázuriz', 'Eduardo Errázuriz Larraín', 'Olavarría Bravo'], 1:['^$']}[rep]

        partidos = {'Partido Radical':{0:['Vásquez Rodríguez'], 1:['^$']}[rep],
                    'Partido Nacional':{0:['Serrano Menchaca', 'Carlos León Palma'], 1:['^$']}[rep],
                    'Partido Conservador': {0:['Eduardo Errázuriz Larraín'], 1:['^$']}[rep],
                    'Partido Demócrata':{0:['Estay Cortés'], 1:['^$']}[rep],
                    #
                    'Partido Liberal Aliancista':{0:['Villarroel Mora', 'Merino Esquivel', 'Alberto Vial Infante', 'Ernesto Barros Jarpa', 'Correa Roberts', 'Olavarría Bravo',  'González Verdugo', 'Greek Cross', 'Palacios Baeza', 'Maza Fernández', 'Grob Westermeyer', 'Espejo Pando', 'Jaramillo Valderrama', 'Silva Sepúlveda', 'Manuel Rivas Vicuña'], 1:['^$']}[rep],
                    'Partido Liberal Unionista':{0:['Héctor Claro Salas', 'Ismael Edwards Matte', 'Diego Francisco Bulnes Correa', 'Jorge Astaburuaga Lyon', 'Pérez Peña', 'Máximo Valdés Fontecilla', 'Mujica Valenzuela', 'Santa María Cerveró', 'Germán Ignacio Riesco Errázuriz', 'Francisco Valdés Cuadra'], 1:['^$']}[rep],
                    'Partido Liberal Democrático Aliancista':{0:['de la Cuadra Poisson', 'Luis R. Fuenzalida', 'Barbosa Baeza', 'Alberto Collao', 'de la Jara Zúñiga', 'Agustín Correa Bravo',  'del Canto Medán', 'Rubio Domínguez'], 1:['^$']}[rep],
                    'Partido Liberal Democrático Unionista':{0:['Urzúa Jaramillo', 'Ramón Luis Ossa Videla',  'Lisoni Mac-Clure', 'Absalón Valencia', 'Herquíñigo Gómez', 'Solar Urrutia',  'Marín Alemany', 'Alejandro Salinas'], 1:['^$']}[rep]
                    }

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Solar Urrutia')):
            candidatos.loc[len(candidatos.index),:] = 'Parral','','Domingo Antonio Solar Urrutia','Partido Liberal Democrático Unionista','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Domingo_Antonio_Solar_Urrutia'

        if (rep == 1):
            if not sum(candidatos['Candidatos'].str.contains('Julio Buschmann von Desauer')):
                candidatos.loc[len(candidatos.index),:] = 'Llanquihue','','Julio Buschmann von Desauer','Partido Radical','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Julio_Buschmann_Von_Desauer'
            candidatos.loc[len(candidatos.index),:] = 'Ñuble','','Juan Serrano Squella','Partido Liberal','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Serrano_Squella'

            candidatos = candidatos[~candidatos['Candidatos'].isin(['Jorge Errázuriz Tagle', 'Arturo Besa Navarro'])]
        
    if eleccion == 1921:
        #fuente: la nacion, 6 y 8/marzo/1924
        reemplazados = {0:['Silva Cortés'], 
                        1:['Armando Quezada Acharán', 'Jorge Errázuriz Tagle', 'Arturo Besa Navarro', 'Malaquías Concha Ortiz', 
                           'Zenón Torrealba Ilabaca', 'Enrique Mac-Iver Rodríguez', 'José Pedro Alessandri Palma']}[rep]
        reemplazantes = {0:['Tizzoni Lucciano'], 
                         1:['Ismael Tocornal Tocornal', 'Eduardo Opaso Letelier', 'Romualdo Silva Cortés', 'Luis Enrique Concha González']}[rep]
        presuntivos = {0:['Eduardo Opaso Letelier'], 1:['^$']}[rep]

        partidos = {'Partido Demócrata':{0:['Luis Correa Ramírez', 'Gutiérrez Vidal'], 1:['Luis Enrique Concha González']}[rep],
                    'Partido Conservador':{0:['Marín Pinuer'], 1:['^$']}[rep],
                    'Partido Nacional Aliancista': {0:['Cornelio Saavedra'], 1:['^$']}[rep],
                    'Partido Radical': {0:['Azócar Álvarez'], 1:['^$']}[rep],
                    #
                    'Partido Liberal Aliancista':{0:['Mujica Mardones', 'Ramírez Frías', 'Correa Roberts', 'Jaramillo Valderrama', 'Moreno Correa', 'Garcés Gana', 'Silva Sepúlveda', 'Maza Fernández', 'Domingo Matte Larraín', 'Escobar Morales', 'Cordero Albano', 'Cortés Silva'], 1:['^$']}[rep],
                    'Partido Liberal Unionista':{0:['Héctor Claro Salas', 'Diego Francisco Bulnes Correa', 'Ismael Edwards Matte', 'Guillermo Edwards Matte', 'Bunster Villagra', 'Eduardo Opaso Letelier', 'Lillo Aztorquiza', ' Claro Lastarria'], 1:['^$']}[rep],
                    'Partido Liberal Democrático Aliancista':{0:['Cubillos Pareja', 'Agustín Correa Bravo', 'Balmaceda Toro'], 1:['^$']}[rep],
                    'Partido Liberal Democrático Unionista':{0:['Sánchez García de la Huerta', 'Urzúa Jaramillo', 'Absalón Valencia',  'Silva Somarriva', 'Pedro Opaso Letelier', 'Herquíñigo Gómez', 'Alberto Collao', 'de la Jara Zúñiga', 'Lisoni Mac-Clure'], 1:['^$']}[rep]
                    }
                
        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Hormann Soruco')):
            candidatos.loc[len(candidatos.index),:] = 'Ovalle','','José Antonio Echavarría Tagle','Partido Nacional','','','','','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Antonio_Echavarría_Tagle'
            candidatos.loc[len(candidatos.index),:] = 'Santiago','','Jorge Hörmann Soruco','Partido Nacional','','','*','*',''        
            candidatos.loc[len(candidatos.index),:] = 'Santiago','','Paulo Marín Pinuer','Partido Nacional','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Paulo_Marín_Pinuer'

        if (rep == 1):
            if not sum(candidatos['Candidatos'].str.contains('Malaquías Concha Ortiz')):
                candidatos.loc[len(candidatos.index),:] = 'Concepción','','Malaquías Concha Ortiz','Partido Demócrata','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Malaquías_Concha_Ortiz'            

            candidatos = candidatos[~candidatos['Candidatos'].isin(['Roberto Lyon Santa María', 'Fernando Liborio Lazcano Echaurren', 'Samuel González Julio', 'José María Valderrama Lira'])]
    
    #revisar: falta malaquias concha ortiz, reemplazado por enrique concha gonzalez en 1921
    if eleccion == 1918:
        reemplazados = {0:['Vial Solar', 'Acuña Valdivia'], 
                        1:['Pedro Vicente Reyes Palazuelos', 'Roberto Lyon Santa María', 'Fernando Liborio Lazcano Echaurren', 'Samuel González Julio', 'José María Valderrama Lira',
                           'Arturo Alessandri Palma']}[rep]
        reemplazantes = {0:['Javier Bustamante', 'Paredes Pacheco'], 
                         1:['Juan Enrique Concha Subercaseaux', 'Alberto Félix del Carmen González Errázuriz', 'Ladislao Errázuriz Lazcano', 'Pedro Segundo Letelier Silva', 'Ricardo Valdés Bustamante']}[rep]
        presuntivos = {0:['Juliet Ossa', 'Balmaceda Saavedra'], 1:['^$']}[rep]
        
        partidos = {'Partido Liberal': {0:['Somarriva Undurraga', 'Lorenzo Montt Montt', 'Máximo Valdés Fontecilla', 'Garcés Gana', 'Eduardo Opaso Letelier', 'Pedro Felipe Iñíguez Larraín'], 1:['^$']}[rep],
                    'Partido Liberal Democrático': {0:['Manuel Vargas', 'Lisoni Mac-Clure', 'Alfredo Riesco Riesco', 'Cubillos Pareja', 'Díaz Garcés'], 1:['^$']}[rep],
                    'Partido Liberal Democrático Aliancista':{0:['Balmaceda Toro'], 1:['^$']}[rep],
                    #
                    'Partido Demócrata': {0:['Bañados Honorato', 'Gutiérrez Vidal'], 1:['^$']}[rep],
                    'Partido Nacional': {0:['José Manuel Larraín Valdés'], 1:['^$']}[rep],
                    'Partido Nacional Aliancista': {0:['Reyes del Río'], 1:['^$']}[rep],
                    'Partido Conservador': {0:['Javier Bustamante'], 1:['^$']}[rep]                    
                    }
        
        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Díaz Garcés')):
            candidatos.loc[len(candidatos.index),:] = 'Laja','','Joaquín del Tránsito Díaz Garcés','Partido Nacional','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Joaquín_Del_Tránsito_Díaz_Garcés'
            candidatos.loc[len(candidatos.index),:] = 'Castro','','Juan Rafael del Canto Medán','Partido Liberal','','','','','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Juan_Rafael_Del_Canto_Medán'

        if (rep == 1):        
            if not sum(candidatos['Candidatos'].str.contains('Malaquías Concha Ortiz')):
                candidatos.loc[len(candidatos.index),:] = 'Concepción','','Malaquías Concha Ortiz','Partido Demócrata','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Malaquías_Concha_Ortiz'            
    
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Luis Enrique Concha González'])]

    if eleccion == 1915:
        reemplazados = {0:['Cortés Cabezas','Eyzaguirre Rouse', 'Pozo Urzúa', 'Bahamonde Hoppe'], 
                        1:['Juan Luis Sanfuentes Andonaegui', 
                           'Francisco Valdés Vergara', 'Manuel Salinas González']}[rep]
        reemplazantes = {0:['Silva Endeiza', 'Ibáñez Ibáñez', 'Hederra Concha', 'Coveña Donoso'], 
                         1:['Alfredo Escobar Campaña']}[rep]
        presuntivos = {0:[ 'Barrios Castellón'], 1:['^$']}[rep]

        # fuente: urzua valenzuela, p.400
        # falta la militancia de: manuel hederra concha, quién ingresó el 2/3/1916 (según anales.cl era nacional), daniel barrios castellón
        partidos = {'Partido Nacional': {0:['Prat Carvajal', 'Irarrázaval Smith', 'Letelier Espínola', 'Pozo Urzúa', 'Wenceslao del Real', 'Döll Rojas'], 1:['^$']}[rep],
                    'Partido Radical': {0:['Rivera Alcayaga', 'Videla Cortés', 'Vital Sánchez', 'Coveña Donoso', 'Fernández Iñíguez', 'Anguita Anguita'], 1:['^$']}[rep], 
                    'Partido Conservador': {0:['Urrejola Mulgrew', 'Subercaseaux Pérez'], 1:['^$']}[rep],
                    'Partido Liberal': {0:['Matte Larraín', 'Orrego Barros', 'Concha Cienfuegos', 'Zepeda Perry'], 1:['^$']}[rep],
                    'Partido Liberal Democrático': {0:['Cubillos Pareja', 'Urzúa Jaramillo', 'Freire García de la Huerta'], 1:['^$']}[rep],
                    'Partido Liberal Doctrinario': {0:['Iñíguez Larraín'], 1:['^$']}[rep],
                    'Partido Demócrata': {0:['Cárdenas Avendaño'], 1:['^$']}[rep]
                    }
        
        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Concha Ortiz')):
            candidatos.loc[len(candidatos.index),:] = 'Temuco','','Malaquías Concha Ortiz','Partido Demócrata','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Malaquías_Concha_Ortiz'

        if (rep == 1):
            candidatos = candidatos[~candidatos['Candidatos'].isin(['José Adolfo Ricardo Matte Pérez', 'Juan Enrique Concha Subercaseaux'])]

    ## REVISAR                        
    if eleccion == 1912:
        reemplazados = {0:['Maira González', 'Gallardo González'], 
                        1:['José Adolfo Ricardo Matte Pérez', 
                           'José Luis Tocornal Jordán']}[rep]
        reemplazantes = {0:['Castellón Larenas', 'Barrios Ugalde'], 
                         1:['Francisco Valdés Vergara']}[rep]
        presuntivos = {0:['Contreras Sotomayor', 'Ismael Vicuña Subercaseaux', 'Luis Aurelio Pinochet', 'Rivera Ojeda', 'Möhr Pérez', 'Undurraga Laso'], 1:['^$']}[rep]

        candidatos.loc[candidatos['Candidatos'].str.contains('Contreras Sotomayor'), 'Partido'] = '' #dice «Alianza Liberal»

        # faltan las militancias de Rafael ugarte vial, matias silva sepulveda (PL?) y Francisco bunster
        partidos = {'Partido Radical': {0:['Rivera Alcayaga', 'Rivera González', 'Anguita Anguita'], 1:['^$']}[rep], 
                    'Partido Liberal': {0:['Arteaga Ureta'], 1:['^$']}[rep],
                    'Partido Liberal Democrático': {0:['Alfredo Riesco Riesco', 'Arturo Urzúa Rojas', 'Ramírez Sanz', 'Urzúa Jaramillo'], 1:['^$']}[rep],
                    'Partido Nacional': {0:['Bustos Mora', 'Samuel Pozo Urzúa'], 1:['^$']}[rep],
                    'Partido Demócrata': {0:['Cárdenas Avendaño'], 1:['^$']}[rep],
                    'Partido Conservador': {0:['Ramón Guillermo del Carmen Subercaseaux Pérez'], 1:['^$']}[rep],
                    }

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Concha Ortiz')):
            candidatos.loc[len(candidatos.index),:] = 'Concepción','','Malaquías Concha Ortiz','Partido Demócrata','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Malaquías_Concha_Ortiz'
            candidatos.loc[len(candidatos.index),:] = 'Laja','','Francisco Bunster','','','','*','*',''

        if (rep == 1):
            candidatos = candidatos[~candidatos['Candidatos'].isin(['José Rafael del Carmen Balmaceda Fernández', 'Alfredo Escobar Campaña'])]
        
    # liberales aliancistas mantuvieron dos diputaciones?
    if eleccion == 1909:
        reemplazados = {0:['Suárez Mujica', 'Edwards Mac-Clure', 'Rivas Ramírez', 'Foster Recabarren', 'Pereira Gandarillas', 'Figueroa Larraín', 'Rivera Ojeda', 'Irarrázaval Zañartu', 'Manterola de la Fuente'], 
                        1:['José Rafael del Carmen Balmaceda Fernández', 'Domingo Atanasio Fernández Concha']}[rep]
        reemplazantes = {0:['Gandarillas Matta', 'Larraín Valdés','Gutiérrez Martínez', 'Foster Recabarren', 'Silva Cortés', 'Sánchez García de la Huerta', 'Pinto Cruz', 'Smitmans Rothamel', 'Rivera González'], 
                         1:['Juan Eduardo Mackenna Astorga', 'Ernesto Alberto Hübner Bermúdez']}[rep]
        presuntivos = {0:['León Silva', 'Juan de Dios Morandé Vicuña'], 1:['^$']}[rep]

        partidos = {'Partido Conservador': {0:['Eguiguren Valero', 'Enrique Morandé Vicuña', 'Ramón Guillermo del Carmen Subercaseaux Pérez', 'Darío Urzúa Rojas'], 1:['^$']}[rep],
                    'Partido Liberal': {0:['Irarrázaval Zañartu', 'Manuel García de la Huerta Izquierdo', 'Roldán Álvarez', 'Rivera Ojeda', 'Carlos A. Sanhueza', 'Paulino Alfonso del Barrio'], 1:['^$']}[rep],
                    'Partido Liberal Democrático': {0:['Ramírez Sanz', 'Arturo Urzúa Rojas'], 1:['^$']}[rep],
                    'Partido Demócrata': {0:['Araya Araya'], 1:['^$']}[rep],
                    'Partido Radical': {0:['Rivera Alcayaga', 'Samuel González Julio'], 1:['^$']}[rep], 
                    'Partido Nacional': {0:['Bustos Mora', 'José Manuel Pozo Urzúa'], 1:['^$']}[rep],
                    }
        
        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Concha Ortiz')):
            candidatos.loc[len(candidatos.index),:] = 'Concepción','','Malaquías Concha Ortiz','Partido Demócrata','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Malaquías_Concha_Ortiz'

        if (rep == 1):
            if not sum(candidatos['Candidatos'].str.contains('Domingo Atanasio Fernández Concha')):
                candidatos.loc[len(candidatos.index),:] = 'Maule','','Domingo Atanasio Fernández Concha','Partido Conservador','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Domingo_Atanasio_Fernández_Concha'
            candidatos.loc[len(candidatos.index),:] = 'Aconcagua','','Rafael Segundo Sotomayor Gaete','Partido Radical','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Rafael_Segundo_Sotomayor_Gaete'

            candidatos = candidatos[~candidatos['Candidatos'].isin(['Federico Varela Cortés-Monroy', 'Pedro Montt Montt', 'Maximiliano Espinosa Pica', 'Ramón Ricardo Rozas Garfias',
                                                                    'Rafael Sotomayor Baeza'])]

    if eleccion == 1906:
        reemplazados = {0:['Cruz Díaz', 'Pinto Agüero', 'Sanfuentes Moreno', 'Valenzuela Larenas'], 
                        1:['Federico Varela Cortés-Monroy', 'Pedro Montt Montt', 'Maximiliano Espinosa Pica', 'Ramón Ricardo Rozas Garfias',
                           'Adolfo Eastman Quiroga', 'Federico Puga Borne', 'Federico Varela Cortés-Monroy']}[rep]
        reemplazantes = {0:['Agustín Edwards Mac-Clure', 'García de la Huerta Izquierdo', 'Balmaceda Toro', 'Figueroa Larraín'], 
                         1:['Joaquín Figueroa Larraín', 'Joaquín Walker Martínez', 'Luis Antonio Vergara Ruiz', 'José Francisco Fabres Ríos']}[rep]
        presuntivos = {0:['Recabarren Serrano'], 
                       1:['^$']}[rep]

        partidos = {'Partido Conservador': {0:['Concha Subercaseaux' ,'Vial Carvallo', 'Darío Urzúa Rojas'], 1:['^$']}[rep],
                    'Partido Liberal': {0:['Rivera Ojeda', 'Irarrázaval Zañartu', 'Zañartu Fierro'], 1:['^$']}[rep], 
                    'Partido Liberal Democrático': {0:['Ossa Ossa', 'Salas Lavaquí'], 1:['^$']}[rep],
                    'Partido Radical': {0:['Lorca Marcoleta', 'Samuel González Julio', 'Jorge E. Guerra Vergara'], 1:['^$']}[rep],
                    'Partido Nacional':  {0:['José Víctor Besa Navarro', 'José Bonifacio Vergara Correa'], 1:['^$']}[rep], 
                    'Partido Demócrata': {0:['Leiva Rodríguez'], 1:['^$']}[rep],
                    }

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Concha Ortiz')):
            candidatos.loc[len(candidatos.index),:] = 'Concepción','','Malaquías Concha Ortiz','Partido Demócrata','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Malaquías_Concha_Ortiz'

        if (rep == 1):
            if not sum(candidatos['Candidatos'].str.contains('Domingo Atanasio Fernández Concha')):
                candidatos.loc[len(candidatos.index),:] = 'Maule','','Domingo Atanasio Fernández Concha','Partido Conservador','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Domingo_Atanasio_Fernández_Concha'
            candidatos.loc[len(candidatos.index),:] = 'Aconcagua','','Rafael Segundo Sotomayor Gaete','Partido Radical','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Rafael_Segundo_Sotomayor_Gaete'
                
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Carlos Walker Martínez', 'Carlos Correa Toro',
                                                                    'Ernesto Alberto Hübner Bermúdez', 'Rafael Sotomayor Baeza'])]

    if eleccion == 1903:
        reemplazados = {0:['Figueroa Larraín', 'Errázuriz Echenique', 'Pinto Izarra', 'Ríos González', 'Vásquez Guarda'], 
                        1:['Carlos Walker Martínez', 'Carlos Correa Toro', 'Juan Antonio González Ibieta']}[rep]
        reemplazantes = {0:['Walker Martínez', 'Francisco Echenique Gandarillas', 'Yáñez Ponce de León', 'Zañartu Prieto', 'Huneeus Gana'], 
                         1:['Javier Ángel Figueroa Larraín', 'Carlos Irarrázaval Larraín', 'Juan Castellón Larenas']}[rep]
        presuntivos = {0:['Valdés Vergara', 'Aldunate Bascuñán', 'Larraín Alcalde', 'Armanet Vergara', 'Germán Munita', 'Leiva Rodríguez', 'Gacitúa Brieba', 'José Miguel Echenique Gandarillas'], 
                       1:['^$']}[rep]

        partidos = {'Partido Liberal Democrático': {0:['Ossa Ossa', 'Enrique Vicuña Subercaseaux', 'Salas Lavaquí', 'Vergara Ruiz'], 1:['^$']}[rep],
#                    'Partido Liberal Doctrinario': {0:['Renato Sánchez García de la Huerta'], 1:['^$']}[rep],
                    'Partido Radical': {0:['Lorca Marcoleta', 'Plummer de Ferari', 'Samuel González Julio'], 1:['^$']}[rep],
                    'Partido Demócrata': {0:['Artemio Gutiérrez'], 1:['^$']}[rep],
                    'Partido Conservador': {0:['Ruiz Valledor', 'Darío Urzúa Rojas'], 1:['^$']}[rep],
                    }

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Concha Ortiz')):
            candidatos.loc[len(candidatos.index),:] = 'Concepción','','Malaquías Concha Ortiz','Partido Demócrata','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Malaquías_Concha_Ortiz'

        if (rep == 1):
            if not sum(candidatos['Candidatos'].str.contains('José Eugenio Guzmán Irarrázaval')):
                candidatos.loc[len(candidatos.index),:] = 'Arauco','','José Eugenio Guzmán Irarrázaval','Partido Liberal','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Eugenio_Guzmán_Yrarrázaval'            
                        
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Germán Riesco Errázuriz', 'Aníbal Zañartu Zañartu', 'Eliodoro Yáñez Ponce de León', 'Eduardo Matte Pérez'])]
        
    if eleccion == 1900:
        reemplazados = {0:['Bello Codesido', 'Mac Clure Ossandón', 'Walker Martínez', 'del Río Villalobos'], 
                        1:['Aníbal Zañartu Zañartu', 'Eduardo Matte Pérez', 'Germán Riesco Errázuriz']}[rep]
        reemplazantes = {0:['Vicuña Subercaseaux', 'Bascuñán Santa María', 'Landa Zárate', 'Aldunate Bascuñán'], 
                         1:['Enrique Mac-Iver Rodríguez', 'Juan Luis Sanfuentes Andonaegui', 'Pedro Segundo Letelier Silva']}[rep]
        presuntivos = {0:['Pleiteado Cevallos', 'Blanlot Holley', 'Manuel Veillon', 'Hevia Riquelme', 'Echaurren Valero', 'Burgos Figueroa', 'Corbalán Melgarejo'], 
                       1:['Eliodoro Yáñez Ponce de León']}[rep]

        partidos = {'Partido Demócrata': {0:['Artemio Gutiérrez', 'Landa Zárate'], 1:['^$']}[rep],
                    'Partido Radical': {0:['Vivanco Toro', 'Feliú Manterola'], 1:['^$']}[rep],
                    }
        
        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Concha Ortiz')):
            candidatos.loc[len(candidatos.index),:] = 'Concepción','','Malaquías Concha Ortiz','Partido Demócrata','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Malaquías_Concha_Ortiz'
        
        if (rep == 1):
            if not sum(candidatos['Candidatos'].str.contains('José Eugenio Guzmán Irarrázaval')):
                candidatos.loc[len(candidatos.index),:] = 'Arauco','','José Eugenio Guzmán Irarrázaval','Partido Liberal','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Eugenio_Guzmán_Yrarrázaval'            
            
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Juan Castellón Larenas'])]
                    
    if eleccion == 1897:
        reemplazados = {0:['Salinas González', 'Bañados Espinosa'], 
                        1:['Guillermo Matta Goyenechea', 'Javier García-Huidobro Eyzaguirre', 'José María Balmaceda Fernández']}[rep]
        reemplazantes = {0:['Robinet Lambarri', 'Pérez Montt'], 
                         1:['Juan Castellón Larenas', 'Rafael Valentín Errázuriz Urmeneta', 'Federico Varela Cortés-Monroy']}[rep]
        presuntivos = {0:['Alemany Sánchez', 'Sánchez Massenlli', 'Alberto Sanfuentes Moreno', 'Concha Ortiz'], 
                       1:['^$']}[rep]

        partidos = {'Partido Demócrata': {0:['Artemio Gutiérrez'], 1:['^$']}[rep],
                    }

        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Herboso España')):
            candidatos.loc[len(candidatos.index),:] = 'Rancagua','','Francisco Herboso España','Partido Liberal Democrático','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Francisco_Herboso_España'
            candidatos.loc[len(candidatos.index),:] = 'Concepción','','Malaquías Concha Ortiz','Partido Demócrata','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Malaquías_Concha_Ortiz'        
        
        if (rep == 1):
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Manuel José Irarrázaval Larraín', 'Federico Errázuriz Echaurren', 'Vicente Segundo Sanfuentes Moreno',
                                                                    'Eliodoro Gormaz Carrera'])]

            if not sum(candidatos['Candidatos'].str.contains('Domingo Atanasio Fernández Concha')):
                candidatos.loc[len(candidatos.index),:] = 'Chiloé','','Domingo Atanasio Fernández Concha','Partido Conservador','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Domingo_Atanasio_Fernández_Concha'

    if eleccion == 1894:
        reemplazados = {0:['Walker Martínez', 'Mathieu Andrews'], 
                        1:['Manuel José Irarrázaval Larraín', 'Federico Errázuriz Echaurren', 'Vicente Segundo Sanfuentes Moreno']}[rep]
        reemplazantes = {0:['Aldunate Bascuñán', 'Fredes Ortiz'], 
                         1:['Ventura Blanco Viel', 'Juan Antonio González Ibieta', 'Domingo Atanasio Fernández Concha']}[rep]
        presuntivos = {0:['Richard Fontecilla'], 
                       1:['^$']}[rep]
        
        if rep == 0:
            candidatos.loc[candidatos['Candidatos'].isin(['Enrique Richard Fontecilla']), 'Distrito'] = 'Ovalle'
                
            if not sum(candidatos['Candidatos'].str.contains('Herboso España')):
                candidatos.loc[len(candidatos.index),:] = 'Copiapó','','Alfredo Délano Rojas','Partido Radical','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Alfredo_Délano_Rojas'
                candidatos.loc[len(candidatos.index),:] = 'Rancagua','','Francisco Herboso España','Partido Liberal Democrático','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Francisco_Herboso_España'
                candidatos.loc[len(candidatos.index),:] = 'Yungay','','Juan Enrique Tocornal Doursther','Partido Conservador','','','*','*',''
        
        else:        
            candidatos.loc[candidatos['Candidatos'].isin(['Federico Varela Cortés-Monroy']), 'Circunscripción'] = 'Antofagasta'
            candidatos.loc[candidatos['Candidatos'].isin(['Juan Castellón Larenas']), 'Circunscripción'] = 'Concepción'

            if not sum(candidatos['Candidatos'].str.contains('José Clemente Cecilio Fabres Fernández de Leiva')):
                candidatos.loc[len(candidatos.index),:] = "O'Higgins",'','José Clemente Cecilio Fabres Fernández de Leiva','Partido Conservador','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Clemente_Cecilio_Fabres_Fernández_de_Leiva'
                candidatos.loc[len(candidatos.index),:] = 'Chiloé','','Domingo Atanasio Fernández Concha','Partido Conservador','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Domingo_Atanasio_Fernández_Concha'
            candidatos.loc[len(candidatos.index),:] = 'Tarapacá','','Ramón Barros Luco','Partido Liberal','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Ramón_Barros_Luco'
                
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Manuel Antonio Matta Goyenechea', 'Rafael Valentín Errázuriz Urmeneta', 'Eliodoro Gormaz Carrera'])] 

    if eleccion == 1891:
        reemplazados = {0:['^$'], 
                        1:['Manuel Antonio Matta Goyenechea', 'Waldo Silva Algue', 'Jovino Novoa Vidal', 'Manuel Amunátegui Aldunate',
                           'Adolfo Valderrama Sainz de la Peña']}[rep]
        reemplazantes = {0:['^$'], 
                         1:['Ramón Barros Luco', 'Guillermo Matta Goyenechea', 'Alejandro Vial Guzmán', 'Francisco Segundo Puelma Castillo']}[rep]
        presuntivos = {0:['Letelier Silva'], 1:['^$']}[rep]

        partidos = {'Partido Radical': {0:['Silva Whittaker', 'Rodríguez Rozas', 'Robinet Lambarri', 'Tocornal Tocornal', 'González Julio', 'Urrutia Rozas', 'Pleiteado Cevallos', 'Reyes Basso'], 1:['^$']}[rep],
                    'Partido Liberal': {0:['Correa Sanfuentes', 'Valdés Valdés', 'Jordán Tocornal', 'Federico Errázuriz Echaurren', 'González Ibieta', 'Alberto Montt Montt', 'Serrano Vásquez', 'Zegers García-Huidobro', 'Videla Correas', 'Vásquez Larenas'], 1:['^$']}[rep],
                    'Partido Liberal Democrático': {0:['Zavala Varas'], 1:['^$']}[rep],
                    'Partido Nacional': {0:['Pedro Montt Montt'], 1:['^$']}[rep],
                    'Partido Conservador': {0:['Edwards Garriga', 'Matte Pérez', 'Larraín Alcalde', 'González Errázuriz', 'Lisboa Huerta', 'Joaquín Walker Martínez'],  1:['^$']}[rep]
                    }
        
        if (rep == 0) and not sum(candidatos['Candidatos'].str.contains('Tocornal Doursther')):
            candidatos.loc[len(candidatos.index),:] = 'Yungay','','Juan Enrique Tocornal Doursther','Partido Conservador','','','*','*',''
        
        if (rep == 1):            
            if not sum(candidatos['Candidatos'].str.contains('Álvaro José Miguel Covarrubias Ortúzar')):
                candidatos.loc[len(candidatos.index),:] = 'Tarapacá','','Ramón Barros Luco','Partido Liberal','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Ramón_Barros_Luco'
                candidatos.loc[len(candidatos.index),:] = 'Santiago','','Álvaro José Miguel Covarrubias Ortúzar','Partido Liberal','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Álvaro_José_Miguel_Covarrubias_Ortúzar'
                candidatos.loc[len(candidatos.index),:] = 'Santiago','','Francisco Solano Ugarte Zenteno','','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Francisco_Solano_Ugarte_Zenteno'
                candidatos.loc[len(candidatos.index),:] = 'Santiago','','Agustín Ross Edwards','Partido Liberal','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Agustín_Ross_Edwards'
                candidatos.loc[len(candidatos.index),:] = "O'Higgins",'','José Clemente Cecilio Fabres Fernández de Leiva','Partido Conservador','','','*','*','https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/José_Clemente_Cecilio_Fabres_Fernández_de_Leiva'

                
            candidatos = candidatos[~candidatos['Candidatos'].isin(['Jorge Segundo Huneeus Zegers', 'Miguel Castillo Andueza'])]
        
    candidatos = candidatos.drop_duplicates(subset=['Candidatos'], keep="last")
    
    return candidatos, reemplazados, reemplazantes, presuntivos, partidos

