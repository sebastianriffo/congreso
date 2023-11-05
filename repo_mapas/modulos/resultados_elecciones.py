#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Sebastián RIFFO

Extrae/construye la información electoral usando diversas fuentes, mediante 
la función *resultados_parlamentarias*. La información varía según la elección, 
por lo que se observan dos períodos : 

- 1973-2021, con resultados detallados a nivel nacional, extraídos del SERVEL (1989-)
y wikipedia (1973). En el caso de la elección de senadores, la función 
*parlamentarios1973_presente* armoniza la información entre una elección y la anterior, 
para visualizar la conformación de dicha cámara en el mapa final. Igualmente, 
crea un listado de parlamentarios electos.

- 1828-1969, correspondiente a la conformación de la Cámara de Diputados y el Senado. 
Diversas informaciones relativas a los parlamentarios son corregidas mediante 
*parlamentarios1834_1969*. En caso de tener resultados a nivel provincial, 
estos se agregan usando la función *resultados1925_1969*.

"""
from modulos.pactos import pactos_electorales, siglas_partidos
from modulos.division_politica import provincias_chile, num_prov

from modulos.resultados.webscraping import webscraping_parlamentarios, biografiasBCN
from modulos.resultados.nombres import nombres_unicode, nombres_formato_v2
from modulos.resultados.parlamentarios1973_presente import parlamentarios1973_presente
from modulos.resultados.parlamentarios1834_1969 import parlamentarios1834_1969
from modulos.resultados.resultados1925_1969 import resultados1925_1969

import pandas as pd
pd.options.mode.chained_assignment = None

from pathlib import Path
import re
from ast import literal_eval
from itertools import chain

def resultados_parlamentarias(path_datos, eleccion, rep):    
    """
    Webscraping de las elecciones de diputados y/o senadores en 1828-2021, 
    desde los sitios web del SERVEL histórico (1989-2021), wikipedia (1973) y 
    BCN (1828-1969).
    
    Parámetros
    ----------
    path_datos : PosixPath
        Directorio.
    eleccion : int
        Año de la elección.
    rep : int
        Elección de diputados (0) o senadores (1).

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
        Info electoral por candidato, en cada subdivisión. Entre 1828 y 1969 
        se trata de los parlamentarios electos, mientras que desde 1973 en adelante
        es el listado de candidatos.
        indice = ['Distrito' o 'Circunscripción', 'Lista/Pacto', 'Partido']
        columnas = ['Candidatos', 'Votos', 'Porcentaje', 'Electos', 'Electos_comp', 'url']  
        
    (Notar que 'Distrito'/'Circunscripción' y 'Lista/Pacto' siguen un orden categórico.)    
    """        

    if not eleccion in list(chain({1828,1829},range(1831,1925,3),{1925,1930,1932},range(1937,1974,4), range(1989,2022,4))):
        raise Exception('El año ingresado no corresponde a una elección, o bien esta no se encuentra disponible')

    subdivrow = {0:'Distrito', 1:'Circunscripción'}[rep]    
    flag_reload = False
    
    provincias = provincias_chile(eleccion, rep)
    
#%% ARCHIVOS EXISTENTES
    datos_filenames = sorted(path_datos.glob(''.join(['*',{0:'Distrito',1:'Circunscripcion'}[rep],'*'])))
        
    if datos_filenames:
        flag_reload = True

        if (rep == 1 and eleccion < 2005):
            provincias.append('Designados')
                
        for file in datos_filenames: 
            filename = re.split('_|.csv',file.as_posix())[-2]
            
            if ('electos' in filename and eleccion <= 1969) or ('candidatos' in filename and eleccion >= 1973):
                cols = [subdivrow,'Lista/Pacto','Candidatos', 'Partido', 'Votos', 'Porcentaje', 'Electos', 'Electos_comp', 'url'] 

                candidatos = pd.read_csv(file)
                candidatos = candidatos[cols]
                candidatos = candidatos.fillna('')                  
                
                candidatos['Candidatos'] = candidatos['Candidatos'].apply(lambda x : literal_eval(str(x))).apply(' '.join)
            
            elif ('pp' in filename):
                pp = pd.read_csv(file).fillna('')
                pp[subdivrow] = pd.Categorical(pp[subdivrow], categories=provincias, ordered=False)
                
            elif ('listas' in filename):
                listas = pd.read_csv(file)
                listas[subdivrow] = pd.Categorical(listas[subdivrow], categories=provincias, ordered=False)
                    
#%% WEBSCRAPING CANDIDATOS
    if not datos_filenames or candidatos.empty:
        print('webscraping')
                
        ## webscraping                        
        candidatos = webscraping_parlamentarios(eleccion, rep)
                                            
        ## division electoral
        candidatos = subdiv_prov(provincias, candidatos, eleccion, rep)
                
#%% DFs CANDIDATOS, PACTOS, LISTAS
    candidatos[subdivrow] = pd.Categorical(candidatos[subdivrow], categories=provincias, ordered=False)

    # corrección de tildes, caracteres especiales, apellidos compuestos
    candidatos = nombres_unicode(candidatos)

    # diccionario de partidos-listas
    pactos = pactos_electorales(eleccion)
    estadistica = ['Válidamente emitidos','Nulos','Blancos','Total'] if (eleccion == 1973 or eleccion >= 2013) else (['Válidamente emitidos'] if eleccion >= 1989 else ['Válidamente emitidos','Blancos/Nulos','Total'])
        
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
        candidatos['Electos_comp'] = candidatos['Electos']
        if not 'url' in candidatos.columns: candidatos['url'] = ''
         
        candidatos = candidatos[[subdivrow, 'Lista/Pacto', 'Partido', 'Candidatos', 'Votos', 'Porcentaje', 'Electos', 'Electos_comp', 'url']]
        
        if not flag_reload:                       
            # eventuales inconsistencias en «válidamente emitidos»
            mask_circ = candidatos[candidatos['Lista/Pacto'] == 'Válidamente emitidos'][subdivrow].astype(str).values.tolist()
            
            candidatos.loc[candidatos['Lista/Pacto'] == 'Válidamente emitidos','Votos'] = candidatos[(candidatos['Partido']!= '') & (candidatos[subdivrow].isin(mask_circ))].groupby([subdivrow],sort=False,observed=True).agg({'Votos':'sum'}).astype(int).values   
            candidatos.loc[candidatos['Lista/Pacto'] == 'Total','Votos'] = candidatos[candidatos['Lista/Pacto'].isin(estadistica[0:-1])].groupby([subdivrow],sort=False,observed=True).agg({'Votos':'sum'}).astype(int).values        
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
            
            pp = pp[[subdivrow,'Lista/Pacto','Partido','Candidaturas', 'Votos', 'Porcentaje', 'Electos']]

            pp.loc[pp['Lista/Pacto'].isna(), 'Lista/Pacto'] = pp[pp['Lista/Pacto'].isna()]['Partido'].replace(pactos)
            pp = pp[pp[subdivrow].isin(mask_circ) & ~pp['Partido'].isin(['COSENA','SUPREMA','VIT'])]
                                                         
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
                           
            # 1973: correccion por votos de lista
            if eleccion == 1973:
                listas['Candidaturas'] = listas['Candidaturas'].map(lambda x: x-1 if x>=1 else x)

            listas = listas[[subdivrow,'Lista/Pacto','Candidaturas', 'Votos', 'Porcentaje', 'Electos']]
            listas = listas[listas[subdivrow].isin(mask_circ)]
            
        # Senadores del período pasado van en «candidatos»
        # diputados/senadores reemplazantes van en «electos»       
        (candidatos, electos) = parlamentarios1973_presente(path_datos, candidatos, eleccion, rep)
        electos = nombres_unicode(electos)
            
    else:
        """
        La BCN posee los listados de cada legislatura. Se corrigen y diferencian entre quienes ganaron la elección
        correspondiente y complementarias, para formar el dataframe «candidatos» (llamado así por coherencia).
        Los datos de «partidos» y «listas» se construyen aparte, el primero mediante la función *resultados_pdba*, 
        de estar disponibles.
        """    
                        
        ## cambiar partidos a siglas, generar pactos
        siglas = siglas_partidos()    
        siglas_re = re.compile("|".join(siglas)) 

        ## corregir inconsistencias de la BCN, agregar senadores del período anterior
        candidatos = parlamentarios1834_1969(path_datos, candidatos, eleccion, rep, siglas if flag_reload else None)

        if pactos:
            candidatos['Partido'] = candidatos['Partido'].map(lambda y: siglas[siglas_re.findall(y)[0]] if siglas_re.findall(y) else y)            
            candidatos['Lista/Pacto'] = candidatos['Partido'].map(lambda y: pactos[y] if y in pactos.keys() else '')        
        else:
            siglas_inv = {v: k for k, v in siglas.items()}    
            #futuro: hay que generar «pactos» con los partidos

            candidatos['Lista/Pacto'] = candidatos['Partido'].map(lambda y: siglas_inv[y] if y in siglas_inv.keys() else y) 
            candidatos['Partido'] = candidatos['Partido'].map(lambda y: siglas[siglas_re.findall(y)[0]] if (y != '' and siglas_re.findall(y)) else y)
                
        pp = resultados1925_1969(candidatos, eleccion, rep, pactos, siglas, provincias) if eleccion >= 1925 else None
                
        if pp is not None: 
            listas = pp.copy() 
            listas = listas.groupby([subdivrow, 'Lista/Pacto']).sum().reset_index()
        else: 
            listas = None                
                
    # desde 2013 los nombres vienen en formato «apellido nombre»
    candidatos = nombres_formato_v2(candidatos, formato = (True if flag_reload else (eleccion <= 2009)) )

    if eleccion >= 1973:
        print('Datos BCN candidatos')   
        biografiasBCN(eleccion, rep, candidatos)

    # Lista/Pacto: indice categorico
    cat = list(dict.fromkeys(list(pactos.values()))) if pactos else candidatos['Lista/Pacto'].unique().tolist() 
    cat.extend(estadistica)            
    
    def index_cat(df, cat, rep):
        subdivrow = {0:'Distrito', 1:'Circunscripción'}[rep] 
        
        df['Lista/Pacto'] = pd.Categorical(df['Lista/Pacto'], categories=cat, ordered=True) 
        df.sort_values('Lista/Pacto',inplace=True)  
        df = df.sort_values([subdivrow,'Lista/Pacto'], ascending=[True,True])    
        df = df.set_index([subdivrow,'Lista/Pacto','Partido'] if 'Partido' in df.columns else [subdivrow,'Lista/Pacto'])

        return df
    
    candidatos = index_cat(candidatos, cat[0:-3] if eleccion <= 1969 else cat, rep) 

    if pp is not None:  
        pp = index_cat(pp,cat,rep) 
        listas = index_cat(listas,cat,rep)         
            
        if eleccion >= 1973:        
            # corrección de porcentajes (agregarlos no es suficiente)
            total = estadistica[-1]
    
            pp['Porcentaje'] = round(100*pp['Votos']/(pp.index.get_level_values(subdivrow).map(pp[pp.index.get_level_values('Lista/Pacto').isin([total])].droplevel([1,2])['Votos'])).astype(int),2)
            listas['Porcentaje'] = round(100*listas['Votos']/(listas.index.get_level_values(subdivrow).map(listas[listas.index.get_level_values('Lista/Pacto').isin([total])].droplevel(1)['Votos'])).astype(int),2)
    
#%% GUARDAR DATOS
    prefix_filename = ''.join(['Eleccion',str(eleccion),'_',{0:'Distrito',1:'Circunscripcion'}[rep]])

    candidatos.to_csv(path_datos/(prefix_filename+ ('_candidatos.csv' if eleccion >= 1973 else '_electos.csv') ))          

    if eleccion >= 1973: 
        electos = nombres_formato_v2(electos, formato = (True if flag_reload else (eleccion <= 2009)) )        
        electos = electos.sort_values([subdivrow,'Lista/Pacto'], ascending=[True,True])    
        electos = electos.set_index([subdivrow,'Lista/Pacto','Partido'])
        
        if not flag_reload:            
            electos = pd.merge(electos, candidatos[candidatos['Electos'] == '*'][['Candidatos','url']],
                                how="outer",
                                on=[subdivrow, 'Lista/Pacto', 'Partido','Candidatos', 'url'])
    
            print('Datos BCN electos')   
            biografiasBCN(eleccion, rep, electos)
        
        electos.to_csv(path_datos/(prefix_filename+'_electos.csv'))

    if pp is not None: 
        listas.to_csv(path_datos/(prefix_filename+'_listas.csv'))
        pp.to_csv(path_datos/(prefix_filename+'_pp.csv'))
                       
    return(listas,pp,candidatos)                

#%%
#%%
def subdiv_prov(provincias, candidatos, eleccion, rep):
    """
    Posterior al webscraping, distritos y circunscripciones pueden estar numerados
    o tener nombres propios. Esta función uniformiza sus nombres, siguiendo un 
    listado predefinido.

    Parámetros
    ----------
    provincias : list[str]
        Listado de distritos o circunscripciones.
    candidatos : dataframe
        Info electoral por candidato, en cada subdivisión, luego de ser extraído
        del sitio web correspondiente.
    eleccion : int
        Año de la elección.
    rep : int
        Elección de diputados (0) o senadores (1).

    Entrega
    -------
    candidatos : dataframe
        La columna 'Distrito' o 'Circunscripción' fue modificada usando los 
        nombres presentes en «provincias».

    """
    
    subdivrow = {0:'Distrito', 1:'Circunscripción'}[rep]
    
    if eleccion >= 1925:        
        reg = num_prov(provincias, eleccion, rep)
                                            
        candidatos[subdivrow] = candidatos[subdivrow].replace(dict(zip(reg, provincias)))
                            
    elif eleccion >= 1828:
        candidatos[subdivrow] = candidatos[subdivrow].str.title()
                  
        # inconsistencias en bcn
        if rep == 0:
            candidatos['Distrito'] = candidatos['Distrito'].replace({'San Javier':'Loncomilla', #1876, 1885
                                                                     'Vicuña':'Elqui', #1870
                                                                     'Molina':'Lontué', #1855
                                                                     'Achao':'Quinchao', #1855
                                                                     'Huasco':'Vallenar', #1828            
                                                                     'Colchagua':'San Fernando', #1828
                                                                     #
                                                                     'Los Angeles':'Los Ángeles',
                                                                     'Victoria':'La Victoria'
                                                                     },regex= True)
            if eleccion == 1828:
                candidatos['Distrito'] = candidatos['Distrito'].replace({'Coquimbo':'La Serena'}, regex=True)
            if eleccion == 1849:
                candidatos['Distrito'] = candidatos['Distrito'].replace({'La Laja':'Los Ángeles'}, regex=True)
            if eleccion in {1906, 1909}:
                candidatos['Distrito'] = candidatos['Distrito'].replace({'Santa Cruz':'Curicó'}, regex=True)
    
        agrupaciones_dep = dict(zip(provincias, provincias))
        numeros = re.compile("|".join(agrupaciones_dep))
        candidatos[subdivrow] = candidatos[subdivrow].map(lambda y: agrupaciones_dep[numeros.search(y)[0]] )
            
    return candidatos
