#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Funciones referentes a partidos y pactos electorales.
    - siglas_partidos
    - pactos_electorales
    - leyendas_electorales
    
"""

def siglas_partidos():
    """
    Entrega un diccionario con los nombres de partido y sus respectivas siglas.
    Es utilizado por los módulos resultados_elecciones (al extraer datos de la BCN, 
    entre 1941 y 1969) y mapa_folium (para construir el diagrama parlamentario).

    Entrega
    -------
    siglas : dict[str,str]

    """    
    
    siglas = {'Partido Comunista': 'PC',
              'Partido del Trabajo': 'PT',
              'Partido Progresista Nacional': 'PPN',
              'Partido Socialista Popular': 'PSP',    
              'Partido Socialista Auténtico': 'PSA',
              'Partido Socialista de Trabajadores': 'PST',
              'Partido Socialista': 'PS',             
              'Partido Social Demócrata': 'PSD',
              'Partido Radical Socialista':'PRS',
              'Partido Radical Doctrinario': 'PRDo',                
              'Partido Radical Democrático': 'PRDe',        
              'Partido Radical Social Demócrata': 'PRSD',                                      
              'Partido Radical': 'PR',                
              'Partido Democrático del Pueblo': 'PDP',
              'Partido Democrático Doctrinario': 'PDD',               
              'Partido Democrático Nacional': 'PADENA',    
              'Partido Democrático': 'PDo',   
              'Falange Nacional': 'FN',     
              'Partido Demócrata Cristiano': 'PDC', 
              'Partido Demócrata Nacionalista': 'PDN',                            
              'Partido Demócrata': 'PD',                           
              'Partido Liberal Progresista': 'PLP',
              'Partido Liberal': 'PL',
              'Partido Nacional Cristiano':'PNC',        
              'Partido Nacional':'PN',                
              'Partido Conservador Unido': 'PCU',                
              'Partido Conservador Tradicionalista': 'PCT',
              'Partido Conservador Social Cristiano': 'PCSC',
              'Partido Conservador Cristiano': 'PCC',              
              'Partido Conservador': 'PCon',                 
              'Partido Agrario Laborista': 'PAL', 
              'Partido Agrario': 'PA',
              'Partido Laborista': 'PLa',
              'Partido Femenino Chileno': 'PPF', 
              'Partido Unidad Popular': 'PUP',
              'Acción Nacional': 'AN',
              'Acción Renovadora de Chile': 'AR',              
              'Alianza Popular Libertadora': 'APL',
              'Comandos Populares': 'CP',
              'Democracia Agrario Laborista': 'DAL', 
              'Movimiento Nacional Ibañista': 'MNI',
              'Movimiento Nacional del Pueblo': 'MONAP',
              'Movimiento Social Cristiano': 'MSC',
              'Movimiento Republicano': 'MR',
              'Unión Nacional de Independientes': 'UNI',
              'Unión Nacional Laborista': 'UNL',
              'Unión Socialista Popular': 'USOPO', 
              'Vanguardia Popular Socialista':'VPS',
              'Vanguardia Nacional del Pueblo':'VNP',              
              #
              'Acción Popular Independiente': 'API',
              'Movimiento de Acción Popular Unitaria': 'MAPU', 
              'Izquierda Cristiana': 'IC',
              'Democracia Radical': 'DR',
              'Partido de Izquierda Radical': 'PIR',
              #
              'Consejo de Seguridad Nacional' : 'COSENA',
              'Corte Suprema' : 'SUPREMA', 
              'Vitalicios': 'VIT',
              #
              'Revolución Democrática': 'RD',
              'Convergencia Social': 'CS',
              'Partido Humanista': 'PH',
              'Partido Igualdad': 'IGUALDAD',
              'Partido Comunes': 'COMUNES',
              'Partido Ecologista Verde': 'PEV',
              'Partido Poder': 'PODER',
              'Partido Amplio de Izquierda Socialista': 'PAIS', 
              'Movimiento Amplio Social': 'MAS',
              'Partido Progresista': 'PRO',
              'Partido por la Democracia':'PPD',
              'Partido Regionalista de los Independientes': 'PRI',
              'Federación Regionalista Verde Social': 'FREVS',
              'Partido de la Gente': 'PDG',
              'Renovación Nacional': 'RN',
              'Unión Demócrata Independiente': 'UDI',
              'Evolución Política': 'EVOPOLI',
              'Partido Ciudadanos': 'CIUDADANOS',
              'Unión de Centro-Centro Progresista': 'UCCP',
              'Unión de Centro-Centro': 'UCC',
              'Centro Unido': 'CU',
              'Partido del Sur': 'SUR',
              'Partido de Acción Regionalista': 'PAR',
              'Partido Republicano': 'REPUBLICANO',
              #
              'Independiente':'IND',
              }
    return siglas

#%%
def pactos_electorales(eleccion):
    """
    Información de pactos electorales en el período 1941-2021.
    Notar que para las elecciones de 1961-1969 los pactos no estaban permitidos, 
    sin embargo, estos existían por omisión.

    Parameters
    ----------
    eleccion : int
        Año de la elección.

    Returns
    -------
    pactos : dict[str,str]
        Pacto electoral correspondiente a la elección. 
        Partidos y nombres de listas son keys y values, respectivamente.
    
    """
    
    if eleccion == 2021:
        partidos = ['RN', 'UDI', 'EVOPOLI', 'PRI', 'PDG', 'PTR',
                    'PS', 'PPD', 'PDC', 'CIUDADANOS', 'PR', 'PL', 'PEV', 'UPA',
                    'PH', 'IGUALDAD', 'REPUBLICANO', 'PCC', 'RD', 'COMUNES', 'CS', 'PC', 'FREVS',
                    'NT', 'CU', 'PNC', 'PRO']
        
        listas = ['Chile Podemos +']*4 +['Partido de la Gente', 'Partido de Trabajadores Revolucionarios'] +\
                 ['Nuevo Pacto Social']*6 +['Partido Ecologista Verde', 'Unión Patriótica'] +\
                 ['Dignidad Ahora']*2 +['Frente Social Cristiano']*2 +['Apruebo Dignidad']*5	+\
                 ['Nuevo Tiempo'] +['Independientes Unidos']*2 +['Partido Progresista']
                            
    elif eleccion == 2017:    
        partidos = ['PRO', 'PAIS', 'PTR', 'PH', 'RD', 'IGUALDAD', 'PEV', 'PODER', 'PL',
                    'AMPLITUD', 'CIUDADANOS', 'TODOS', 'FREVS', 'DRP', 'UPA',
                    'PS', 'PPD', 'PRSD', 'PC', 'PDC', 'MAS', 'IC', 'RN', 'UDI', 'EVOPOLI', 'PRI']
            
        listas = ['Por Todo Chile']*2 +['Partido de Trabajadores Revolucionarios'] +['Frente Amplio']*6 +\
                 ['Sumemos']*3 +['Coalición Regionalista Verde']*2 +['Unión Patriótica'] +\
                 ['La Fuerza de la Mayoría']*4 +['Convergencia Democrática']*3 +['Chile Vamos']*4
        
    elif eleccion == 2013: 
        partidos = ['PDC', 'PPD', 'PS', 'PRSD', 'PC', 'MAS', 'ILC', 'PRI', 'PH',
                    'PEV', 'IGUALDAD', 'ILH', 'PL', 'PRO', 'ILI', 'RN', 'UDI', 'ILJ']
        
        listas = ['Nueva Mayoría']*7 +['Partido Regionalista de los Independientes', 'Partido Humanista'] +\
                 ['Nueva Constitución para Chile']*3 +['Si tú quieres, Chile cambia']*3 +['Alianza']*3 
                 
    elif eleccion == 2009: 
        partidos = ['PDC', 'PPD', 'PS', 'PRSD', 'PC', 'IC', 'ILA', 'RN', 'UDI', 'CH1', 'ILB',
                    'PH', 'PEV', 'ILC', 'PRI', 'MAS', 'ILD']
                   
        listas = ['Concertación y Juntos Podemos por más Democracia']*7 +['Coalición por el Cambio']*4 +\
                 ['Nueva Mayoría para Chile']*3 +['Chile Limpio. Vote Feliz']*3 
                 
    elif eleccion == 2005: 
        partidos = ['ANI', 'PAR', 'ILA', 'PDC', 'PPD', 'PS', 'PRSD', 'ILB', 
                    'PC', 'PH', 'ILC', 'RN', 'UDI', 'ILD']
                   
        listas = ['Fuerza Regional Independiente']*3 +['Concertación Democrática']*5 +\
                 ['Juntos Podemos Más']*3 +['Alianza']*3 
                 
    elif eleccion == 2001: 
        partidos = ['PC', 'PH', 'UDI', 'RN', 'ILC', 
                    'PL', 'PDC', 'PPD', 'PS', 'PRSD', 'ILE']
                   
        listas = ['Partido Comunista', 'Partido Humanista'] +['Alianza por Chile']*3 +\
                 ['Partido Liberal'] + ['Concertación']*5 
                 
    elif eleccion == 1997: 
        partidos = ['PH', 'RN', 'UDI', 'SUR', 'ILB', 'PDC', 'PPD', 'PS', 'PRSD', 'ILC',
                    'PC', 'NAP', 'ILD', 'UCCP', 'ILE']
                   
        listas = ['Partido Humanista'] +['Unión por Chile']*4 +['Concertación de Partidos por la Democracia']*5 +\
                 ['La Izquierda']*3 +['Chile 2000']*2
                 
    elif eleccion == 1993: 
        partidos = ['PC', 'MAPU', 'ILA', 'RN', 'UDI', 'UCC', 'SUR', 'PN', 'ILB',
                    'AHV', 'ECOL', 'ILC', 'PDC', 'PPD', 'PS', 'PR', 'SDCH', 'ILD']
                   
        listas = ['Alternativa Democrática de Izquierda']*3 +['Unión por el Progreso de Chile']*6 +\
                 ['La Nueva Izquierda']*3  +['Concertación de Partidos por la Democracia']*6 

    elif eleccion == 1989: 
        partidos = ['PDC', 'PPD', 'PR', 'PH', 'PLV', 'ILA', 'RN', 'UDI', 'ILB', 'SUR', 'ILC',
                    'AN', 'DR', 'ILD', 'PL', 'PS', 'ILE', 'PN', 'ILF',
                    'PAIS', 'PRSD', 'ILG']

        listas = ['Concertación de Partidos por la Democracia']*6 +['Democracia y Progreso']*3 +['Partido del Sur']*2 +\
                 ['Alianza de Centro']*3 +['Liberal-Socialista Chileno']*3 +['Partido Nacional']*2 +\
                 ['Unidad para la Democracia']*3  

    elif eleccion == 1973: 
        partidos = ['PDC', 'PN', 'DR', 'PIR', 'PADENA', 'VL-CODE',
                    'PS', 'PC', 'PR', 'MAPU', 'IC', 'API', 'VL-UP,'
                    'USOPO', 'VL-USOPO']

        listas = ['Confederación de la Democracia']*6 + ['Unidad Popular']*7 +['Unión Socialista Popular']*2 

    elif eleccion == 1969:
        partidos = ['PC', 'PS', 'PSD', 'USOPO', 'PADENA', 'PDC', 'PR', 'PN']
                
        listas = ['Frente de Acción Popular']*3 +['Unión Socialista Popular'] +['Partido Democrático Nacional'] +\
                 ['Partido Demócrata Cristiano'] +['Partido Radical'] +['Partido Nacional']
             
    elif eleccion == 1965:
        partidos = ['VNP', 'PC', 'CP', 'PS', 'PADENA', 'PDo', 'DAL', 'PDC', 'PR', 'PL', 'PCU', 'AN']
        
        listas = ['Frente de Acción Popular']*5 +['Partido Democrático'] +['Democracia Agrario Laborista'] +\
                 ['Partido Demócrata Cristiano'] +['Partido Radical'] +\
                 ['Derecha Tradicional']*2 +['Acción Nacional']
                        
    elif eleccion == 1961: 
        partidos = ['PC', 'PS', 'PDo', 'PADENA', 'CP', 'PDC', 'UNL', 'PCU', 'PR', 'PL']
        
        listas = ['Frente de Acción Popular']*5 +['Partido Demócrata Cristiano'] +['Unión Nacional Laborista'] +\
                 ['Frente Democrático']*3
        
    elif eleccion == 1957: 
        partidos = ['PR', 'PL', 'PS', 'PSP', 'PDo', 'PT', 'PRDo',
                    'PCU', 'FN', 'PCSC', 'PAL',
                    'PN', 'MR', 'PNC', 
                    'PLa', 'PDD', 'MONAP'] 
        
        listas = ['Partido Radical'] +['Partido Liberal'] +['Frente de Acción Popular']*5 +\
                 ['Partido Conservador Unido'] +['Federación Social Cristiana']*2 +['Partido Agrario Laborista'] +\
                 ['Partido Nacional'] +['Movimiento Republicano'] +['Partido Nacional Cristiano'] +\
                 ['Partido Laborista'] +['Partido Democrático Doctrinario'] +['Movimiento Nacional del Pueblo']

    elif eleccion == 1953:
        partidos = ['PAL', 'PSP', 'PDP', 'PRDo', 'PPF', 'PL', 'PR', 'PCT',
                    'UNI', 'PNC', 'AR', 'PLa', 'MNI', 'PF', 'PS', 'FN',
                    'PCSC', 'PA', 'MONAP',
                    'PDo', 'UNJ', 'PDN',
                    'PUP', 'NAP', 'ACFP',
                    'OC', 'MSC', 'PNA']
        
        listas = ['Alianza Nacional del Pueblo']*5 +['Partido Liberal'] +['Partido Radical'] +['Partido Conservador Tradicionalista']+\
                 ['Federación Nacional de Fuerzas Ibañistas']*6 +['Frente del Pueblo'] +['Falange Nacional'] +\
                 ['Partido Conservador Social Cristiano'] +['Partido Agrario'] +['Movimiento Nacional del Pueblo'] +\
                 ['Partido Democrático de Chile'] +['Unión Nacional de Jubilados'] +['Partido Democrático Nacional'] +\
                 ['Partido de Unidad Popular'] +['Nueva Acción Pública'] +['Asociación Comerciantes Frutos del País'] +\
                 ['Organización Campesina'] +['Movimiento Social Cristiano'] +['Partido Nacional Araucano']    

    elif eleccion == 1949: 
        partidos = ['PR', 'PL', 'PDo', 'PCT', 'PCSC', 'PAL', 'PRDe', 'PS', 'FN',
                    'PSP', 'PLP', 'PDP',
                    'PSA', 'AR', 'PLa', 
                    'PRDo', 'MSC', 'PD']
        
        listas = ['Concentración Nacional']*4 +['Partido Conservador Social Cristiano'] +['Falange Radical Agrario Socialista']*4 +\
                 ['Partido Socialista Popular'] +['Partido Liberal Progresista'] +['Partido Democrático del Pueblo'] +\
                 ['Partido Socialista Auténtico'] +['Acción Renovadora'] +['Partido Laborista'] +\
                 ['Partido Radical Doctrinario'] +['Movimiento Social Cristiano'] +['Partido Demócrata']	
                 
    elif eleccion == 1945:
        partidos = ['PCon', 'PL', 'PLP', 'PA', 'PR', 'PPN', 'PS', 'PDo', 'PSA',
                    'FN', 'APL', 'PD',
                    'PDN', 'PLa']
        
        listas = ['Derecha']*4 +['Alianza Democrática de Chile']*4 +['Partido Socialista Auténtico'] +\
                 ['Falange Nacional'] +['Alianza Popular Libertadora'] +['Partido Demócrata'] +\
                 ['Partido Demócrata Nacionalista'] +['Partido Laborista']

    elif eleccion == 1941:
        #fuente : la nacion, 02/03/1941        
        partidos = ['VPS', 'FN', 'APL',
                    'PCon', 'PL', 'PD', 'PA', 'PR', 'PPN', 'PDo', 'PRS', 'PST', 'PS',
                    'PLa', 'PLPr', 'PRSO', 'PRM'] 
        
        listas = ['Vanguardia Popular Socialista'] +['Falange Nacional'] +['Alianza Popular Libertadora'] +\
                 ['Partido Conservador', 'Partido Liberal', 'Partido Democrático', 'Partido Agrario'] +['Frente Popular']*5 +['Partido Socialista'] +\
                 ['Partido Laborista'] +['Partido Laborista Proletario'] +['Partido Radical Socialista Obrero'] +\
                 ['Partido Regionalista de Magallanes']
    else:
        raise Exception()
        
    pactos = dict(zip(partidos, listas)) 
    pactos['IND'] = 'Candidatura Independiente'    
        
    return pactos

#%%
def leyendas_electorales(eleccion):
    """
    Leyenda a nivel de coaliciones, ordenadas de izquierda a derecha.
    
    Parametros
    ----------
    eleccion : int
        Año de la elección.

    Entrega
    -------
    leyenda : dict[str,str]
        Leyenda correspondiente a la elección, en un diccionario conformado por 
        pactos y colores. 
                
        La elección de colores sigue este patrón general : 
        leyenda = { izquierda   : '#cc0000', #rojo
                    centro-izq1 : '#dd3497', #fucsia claro (frente amplio)
                    centro-izq2 : '#990099', #violeta (socialista)
                    centro-izq3 : '#7aa711', #verde  (radical-concertacion)
                    centro-1    : '#ec7014', #naranjo claro    
                    centro-2    : '#f6cf71', #amarillo pastel
                    centro-der  : '#f7dc6f', #amarillo claro
                    derecha-1   : '#0288d1', #celeste
                    derecha-2   : '#4dd0e1', #turquesa
                    ultra-der   : '#303f9f', #azul
                    }

        Notar que la leyenda no necesariamente incluye a todas las coaliciones.
        Las restantes son procesadas como 'otros' (color café ('#a04000'))
        por *mapa_folium*.        
    """
    
    if eleccion == 2021:
        leyenda = {'Apruebo Dignidad' : '#dd3497',        
                   'Nuevo Pacto Social' : '#7aa711',     
                   'Partido de la Gente' : '#f7dc6f',    
                   "Chile Podemos +" : '#0288d1',        
                   'Frente Social Cristiano' : '#303f9f'}                   
    elif eleccion == 2017:
        leyenda = {'Frente Amplio' : '#dd3497',           
                   'La Fuerza de la Mayoría' : '#7aa711',     
                   'Convergencia Democrática' : '#f6cf71',    
                   'Chile Vamos' : '#0288d1'}                   
    elif eleccion == 2013:
        leyenda = {'Nueva Mayoría' : '#7aa711',     
                   'Alianza' : '#0288d1'}
    elif eleccion == 2009:
        leyenda = {'Concertación y Juntos Podemos por más Democracia' : '#7aa711',     
                   'Coalición por el Cambio' : '#0288d1'}                   
    elif eleccion == 2005:
        leyenda = {'Concertación Democrática' : '#7aa711',     
                   'Alianza' : '#0288d1'}                   
    elif eleccion == 2001:
        leyenda = {'Concertación' : '#7aa711',     
                   'Alianza por Chile' : '#0288d1'}                   
    elif eleccion == 1997:
        leyenda = {'Concertación de Partidos por la Democracia' : '#7aa711',     
                   'Unión por Chile' : '#0288d1'}                   
    elif eleccion == 1993:
        leyenda = {'Concertación de Partidos por la Democracia' : '#7aa711',     
                   'Unión por el Progreso de Chile' : '#0288d1'}                   
    elif eleccion == 1989:
        leyenda = {'Concertación de Partidos por la Democracia' : '#7aa711',     
                   'Democracia y Progreso' : '#0288d1'}
    elif eleccion == 1973:
        leyenda = {'Unidad Popular' : '#cc0000', 
                   'Confederación de la Democracia' : '#0288d1',
                   'Unión Socialista Popular': ''}        
    elif eleccion == 1969:        
        leyenda = {'Frente de Acción Popular' : '#cc0000',
                   'Partido Radical': '#7aa711', 
                   'Partido Demócrata Cristiano': '#f6cf71',
                   'Partido Nacional': '#0288d1'}          
    elif eleccion == 1965: 
        leyenda = {'Frente de Acción Popular' : '#cc0000',
                   'Partido Radical': '#7aa711', 
                   'Partido Demócrata Cristiano': '#f6cf71',
                   'Derecha Tradicional' : '#303f9f'}          
    elif eleccion == 1961:
        leyenda = {'Frente de Acción Popular' : '#cc0000',
                   'Partido Demócrata Cristiano': '#f6cf71',
                   'Frente Democrático' : '#303f9f'} 
    elif eleccion == 1957: 
        leyenda = {'Frente de Acción Popular' : '#cc0000',
                   'Partido Radical': '#7aa711', 
                   'Federación Social Cristiana': '#f6cf71',
                   'Partido Liberal' : '#0288d1',
                   'Partido Agrario Laborista' : '#4dd0e1',
                   'Partido Nacional': '#797ef6',
                   'Partido Conservador Unido' : '#303f9f'}
    elif eleccion == 1953:
        leyenda = {'Frente del Pueblo' : '#cc0000',
                   'Partido Radical': '#7aa711', 
                   'Falange Nacional': '#f6cf71',                   
                   'Alianza Nacional del Pueblo': '#ec7014',                   
                   'Federación Nacional de Fuerzas Ibañistas': '#ec7014',
                   'Movimiento Nacional del Pueblo': '#ec7014',
                   'Partido Liberal' : '#0288d1',                   
                   'Partido Conservador Tradicionalista' : '#797ef6',
                   'Partido Conservador Social Cristiano' : '#303f9f'}
    elif eleccion == 1949:
        leyenda = {'Partido Socialista Popular': '#990099',
                   'Falange Radical Agrario Socialista': '#ec7014', 
                   'Concentración Nacional': '#0288d1',
                   'Partido Conservador Social Cristiano' : '#303f9f'}
    elif eleccion == 1945:    
        leyenda = {'Alianza Democrática de Chile': '#cc0000', 
                   'Falange Nacional': '#f6cf71',
                   'Derecha' : '#303f9f'}        
    elif eleccion == 1941:
        leyenda = {'Frente Popular': '#cc0000',
                   'Partido Socialista': '#990099',
                   'Falange Nacional': '#f6cf71',  
                   'Partido Demócrata' : '#ec7014',
                   'Partido Liberal' : '#0288d1',                   
                   'Partido Agrario': '#4dd0e1',                   
                   'Partido Conservador': '#303f9f'} 

    else: 
        leyenda = None
    
    return leyenda