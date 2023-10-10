"""
Pequeñas rutinas utilizadas por el módulo *resultados_elecciones*.

- nombres_formato : toma un nombre y lo separa en nombres y apellidos. Esto sirve, 
principalmente, para el diagrama de la nueva legislatura en mapa_parlamentario.
- biografiasBCN : url asociada a cada parlamentario electo, correspondiente a su 
biografía en la BCN, en el período 1989-presente.
"""

import pandas as pd
pd.options.mode.chained_assignment = None

#%%
def nombres_unicode(candidatos, column='Candidatos'):
    """
    Toma la columna 'Candidatos' de un dataframe, para corregir acentos, 
    caracteres especiales, apellidos compuestos y otros errores.

    Parámetros
    ----------
    candidatos : dataframe
        Información de candidatos.
    formato : boolean, opcional
        Por defecto un nombre viene ordenado por nombres y apellidos. 
        'False' si ocurre lo contrario.

    Entrega
    -------
    candidatos : dataframe
        Nombres de candidatos corregidos.

    """
    ## corregir acentos, caracteres especiales y apellidos compuestos         
    nombres = {'Agustin':'Agustín', 'Alvaro':'Álvaro', 'Andres':'Andrés', 'Angel':'Ángel', 'Anibal':'Aníbal', 'Aristides':'Arístides', 'Aristoteles':'Aristóteles',
               'Benjamin':'Benjamín',
               'Cesareo':'Cesáreo', 'Cristian':'Cristián', 'Crisologo':'Crisólogo', 'Cristobal':'Cristóbal',
               'Dario':'Darío',
               'Elias':'Elías', 'Exequias':'Exequías',
               'Felix':'Félix', 'Fermin':'Fermín',
               'Gaston':'Gastón', 'German':'Germán',
               'Hector':'Héctor', 'Hernan':'Hernán', 'Hermogenes':'Hermógenes', 'Hilarion':'Hilarión', 'Hipolito':'Hipólito',
               'Ines':'Inés', 'Ivan':'Iván',
               'Jeronimo':'Jerónimo', 'Jesus':'Jesús', 'Joaquin':'Joaquín', 'Jose':'José', 
               'Leóncio':'Leoncio', 'Leonidas':'Leónidas',
               'Maria':'María', 'Maríana':'Mariana', 'Maríano':'Mariano', 'Martin':'Martín', 'Maximo':'Máximo', 'Moises':'Moisés',
               'Matias':'Matías', 'Monica':'Mónica',                       
               'Nicolas':'Nicolás',
               'Oscar':'Óscar',
               'Pacifico':'Pacífico', 'Pantaleon':'Pantaleón',
               'Ramon':'Ramón', 'Raul':'Raúl', 'Renan':'Renán', 'Rene':'René', 'Ruben':'Rubén',
               'Sebastian':'Sebastián', 'Serafin':'Serafín', 'Sotero':'Sótero',
               'Telesforo':'Telésforo', 'Teofilo':'Teófilo', 'Tomas':'Tomás', 'Tristan':'Tristán',
               'Valentin':'Valentín', 'Victor':'Víctor', 'Víctorino':'Victorino',
               'Zenon':'Zenón', 'Zosimo':'Zócimo'
               }    
    nombres_regex = {'\\b'+x+'\\b' : nombres[x] for x in nombres.keys()}

    articulos = {' Y ':' y ',
                  ' De La ':' de la ', ' De Los ':' de los ', ' De Las ':' de las ', ' De ':' de ', ' Del ':' del ', 
                  ' Van ':' van ', ' Von ':' von ', '-Von ':'-von '
                  }    
    
    apellidos = {'Aguero':'Agüero', 'Aguila':'Águila', 'Aguillon':'Aguillón', 'Aguilo':'Aguiló', 'Alamos':'Álamos', 'Alarcon':'Alarcón', 'Albarran':'Albarrán', 'Alcerreca':'Alcérreca', 'Alvarez':'Álvarez', 'Amunategui':'Amunátegui', 'Antunez':'Antúnez', 'Argandona':'Argandoña', 'Aristegui':'Arístegui', 'Ariztia':'Ariztía', 'Arostegui':'Aróstegui', 'Arriaran':'Arriarán', 'Avalos':'Ávalos', 'Avila':'Ávila', 'Azua':'Azúa',
                 'Balbontin':'Balbontín', 'Banados':'Bañados', 'Barcelo':'Barceló', 'Bascunan':'Bascuñán', 'Bascuñan':'Bascuñán', 'Beltran':'Beltrán', 'Borgono':'Borgoño', 'Borquez':'Bórquez', 'Briseno':'Briseño', 'Brucher':'Brücher', 'Buchi':'Büchi',
                 'Cabezon':'Cabezón', 'Caceres':'Cáceres', 'Cadiz':'Cádiz', 'Cardenas':'Cárdenas', 'Castellon':'Castellón', 'Chacon':'Chacón', 'Chahuan':'Chahuán', 'Chavez':'Chávez', 'Corbalan':'Corbalán', 'Cousino':'Cousiño',
                 'Dalbora':"D'Albora", 'Danus':'Danús', 'Davila':'Dávila', 'de Rementeria':'de Rementería', 'del Rio':'del Río', 'Diaz':'Díaz', 'Doll':'Döll', 'Duenas':'Dueñas', 'Duran':'Durán',
                 'Echavarria':'Echavarría', 'Echeverria':'Echeverría', 'Echeñique':'Echenique', 'Echiburu':'Echiburú', 'Egana':'Egaña', 'Enriquez':'Enríquez', 'Errazuriz':'Errázuriz', 'Errázurriz':'Errázuriz', 'Escandon':'Escandón', 'Espana':'España', 'Espineira':'Espiñeira',
                 'Farias':'Farías', 'Farina':'Fariña', 'Fernandez':'Fernández', 'Forster':'Förster', 'Freí':'Frei', 'Frias':'Frías', 'Frodden':'Frödden',
                 'Gacitua':'Gacitúa', 'Galvez':'Gálvez', 'Garces':'Garcés', 'Garcia':'García', 'Garin':'Garín', 'Garmendia':'Garmendía', 'Gayon':'Gayón', 'Gomez':'Gómez', 'Gonzalez':'González', 'Gundian':'Gundián', 'Gutierrez':'Gutiérrez', 'Guzman':'Guzmán',
                 'Hasbun':'Hasbún', 'Hernandez':'Hernández', 'Herquinigo':'Herquiñigo', 'Hormann':'Hörmann', 'Hubner':'Hübner',
                 'Ibañez':'Ibáñez', 'Ibanez':'Ibáñez', 'Iñiguez':'Iñíguez', 'Iniguez':'Iñíguez', 'Irarrazabal':'Irarrázabal', 'Irarrazaval':'Irarrázaval', 'Irarrazával':'Irarrázaval',
                 'Jordan':'Jordán', 'Jimenez':'Jiménez',
                 'Konig':'König',
                 'Labbe':'Labbé', 'Labrin':'Labrín', 'Larrain':'Larraín', 'Larre':'Larré', 'Larréa':'Larrea', 'Lavaqui':'Lavaquí', 'Lavin':'Lavín', 'Lazon':'Lazón','Leon':'León', 'Leuquen':'Leuquén', 'Lopez':'López',
                 'Macclure':'Mac Clure', 'Maciver':'Mac Iver', 'Mancheno':'Mancheño', 'Marin':'Marín', 'Martinez':'Martínez', 'Marquez':'Márquez', 'Mendez':'Méndez', 'Mendiburu':'Mendiburú', 'Messia':'Messía', 'Mohr':'Möhr', 'Monleon':'Monleón', 'Moran':'Morán', 'Morande':'Morandé', 'Moxo':'Moxó', 'Muhlenbrock':'Mühlenbrock', 'Muller':'Müller', 'Munoz':'Muñoz',
                 'Naveillan':'Naveillán', 'Nuñez':'Núñez', 'Nunez':'Núñez',
                 'O Ryan':"O'Ryan", 'Ochagavia':'Ochagavía', 'Olavarria':'Olavarría', 'Ordenes':'Órdenes', 'Ortíz':'Ortiz', 'Ortuzar':'Ortúzar', 'Ossandon':'Ossandón',
                 'Padin':'Padín', 'Paez':'Páez', 'Paéz':'Páez', 'Patino':'Patiño', 'Pena':'Peña', 'Perez':'Pérez',
                 'Ramirez':'Ramírez', 'Renteria':'Rentería', 'Rincon':'Rincón', 'Rio':'Río', 'Rios':'Ríos', 'Rioseco':'Ríoseco', 'Risopatron':'Risopatrón', 'Rodriguez':'Rodríguez', 'Ruíz':'Ruiz',
                 'Saez':'Sáez', 'Saéz':'Sáez', 'Salamo':'Salamó', 'Saldias':'Saldías', 'Saldivar':'Saldívar', 'Sanchez':'Sánchez', 'Santibañez':'Santibáñez', 'Sepulveda':'Sepúlveda', 'Solis':'Solís', 'Suarez':'Suárez',
                 'Tellez':'Téllez', 'Toha':'Tohá', 'Trucios':'Trucíos',
                 'Ubeda':'Úbeda', 'Urizar':'Urízar', 'Urzua':'Urzúa',
                 'Vallespin':'Vallespín', 'Valdes':'Valdés', 'Vasquez':'Vásquez', 'Velasquez':'Velásquez', 'Vicuna':'Vicuña', 'Vidaurrazaga':'Vidaurrázaga', 'Villagran':'Villagrán', 'Villan':'Villán', 'Vildosola':'Vildósola', 'Vilugron':'Vilugrón',
                 'Woll':'Wöll',
                 'Yañez':'Yáñez', 'Yrarrázaval':'Irarrázaval','Yavar':'Yávar',
                 'Zaldivar':'Zaldívar', 'Zanartu':'Zañartu', 'Zedan':'Zedán', 'Zuñiga':'Zúñiga',
                 #
                 'de Astorga':'Astorga', 'de Ariztía':'Ariztía', 'de Balmaceda':'Balmaceda', 'de Elizondo':'Elizondo', 'de Errázuriz':'Errázuriz', 'de Etcheverz':'Etchevers', 
                 'de Huici':'Huici', 'de Hurtado':'Hurtado', 'de Matta':'Matta', 'de Mira':'Mira', 
                 'de Recabarren':'Recabarren', 'de Velasco':'Velasco', 'de Vicuña':'Vicuña', 'de Zañartu':'Zañartu'
                 }
    # Victoriano  Víctoriano?
    # Villanueva  Villánueva
    # Rioseco Ríoseco
    
    apellidos_regex = {'\\b'+x+'\\b' : apellidos[x] for x in apellidos.keys()}
             
    apellidos_compuestos = {'Cortés de Monroy':'Cortés-Monroy',
                            'Cruz Coke':'Cruz-Coke',
                            'de Santiago Concha':'de Santiago-Concha', 'Cerda Santiago Concha':'Cerda de Santiago-Concha',
                            'García Huidobro':'García-Huidobro',                   
                            'Jocelyn Holt':'Jocelyn-Holt',
                            'Larraín García Moreno': 'Larraín García-Moreno',
                            'Mac Clure': 'Mac-Clure', 'Mac Iver':'Mac-Iver',
                            'Pérez Cotapos':'Pérez-Cotapos',
                            'Viale Rigo':'Viale-Rigo', 'Viera Gallo':'Viera-Gallo',
                            'Ramírez Rivilla':'Ramírez-Rivilla', 'Rigo Righi':'Rigo-Righi', 'Ruiz Tagle':'Ruiz-Tagle', 'Ruiz Esquide':'Ruiz-Esquide'
                            }                        
    
    candidatos[column] = candidatos[column].str.title()

    candidatos[column] = candidatos[column].replace(articulos, regex=True)    
    candidatos[column] = candidatos[column].replace(nombres_regex, regex=True)    
    candidatos[column] = candidatos[column].replace(apellidos_regex, regex=True)
    candidatos[column] = candidatos[column].replace(apellidos_compuestos, regex=True)
    
    ## corregir errores en SERVEL (al 16/01/2023) y nombres incompletos
    candidatos[column] = candidatos[column].replace({'Venturafaulbaum' : 'Ventura Faulbaum', #1989, D58
                                                     'álvarez-Salamán' : 'Álvarez-Salamanca', #1989-97, D38
                                                     'van Rysselbergh Varela' : 'van Rysselberghe Varela', #1997, D44
                                                     'Manouchehr Manouchehri Moghadam Kashan Lobos' : 'Daniel Manouchehri Lobos', #2009, D8
                                                     'DE LAS HERAS DE LAS HERAS' : 'DE LAS HERAS',    #2013, D9
                                                     'KASHAN LOBOS MANOUCHEHRI MOGHADAM' : 'Manouchehri Lobos Daniel' #2021, D5 
                                                     },
                                                     regex=True)       
    
    incongruencias = {'Juan José Aldunate Irarrázabal' : 'Juan José Aldunate Irarrázaval',   
                      'Luis Aguilera Báez' : 'Luis Ernesto Aguilera Báez',
                      'Sergio Aguiló Melo' : 'Sergio Patricio Aguiló Melo',
                      'René Alinco Bustos' : 'René Osvaldo Alinco Bustos',
                      'Amanda Altamirano Guerrero' : 'Amanda Elisa Altamirano Guerrero',
                      'Pedro Álvarez-Salamanca Büchi' : 'Pedro Pablo Álvarez-Salamanca Büchi',
                      'Pedro Alvarado Páez' : 'Pedro Héctor Alvarado Páez',
                      'Pedro Araya Ortiz' : 'Pedro Pablo Araya Ortiz',
                      'Nicanor Araya' : 'Nicanor de la Cruz Araya Araya',
                      'Gabriel Ascencio Mansilla' : 'Gabriel Héctor Ascencio Mansilla',
                      'Raúl Armando Barrionuevo' : 'Raúl Armando Barrionuevo Barrionuevo',
                      'Alejandro Bell Jara' : 'Alejandro Bell Jaras',
                      'Karim Bianchi Retamales' : 'Karim Antonio Bianchi Retamales',
                      'Manuel Cantero Prado' : 'Manuel Segundo Cantero Prado',
                      'Víctor Carmine Zúñiga' : 'Víctor Hernán Carmine Zúñiga', 
                      'Loreto Carvajal Ambiado' : 'María Loreto Carvajal Ambiado',
                      'Eduardo Cerda García' : 'Eduardo Antonio Cerda García',
                      'Sergio Diez Urzúa' : 'Sergio Eduardo de Praga Diez Urzúa',
                      'Eduardo Durán Salinas' : 'Eduardo Alfredo Durán Salinas',
                      'José Ramón Elguero del Campo Bracamonte' : 'José Ramón Elguero del Campo',                                           
                      'Maximiano Errázuriz' : 'Maximiano Errázuriz Eguiguren',
                      'Javier Errázuriz Echaurren':'Francisco Javier Errázuriz Echaurren',
                      'Marcos Espinosa Monardes' : 'Marcos Andrés Espinosa Monardes',                       
                      'Iván Flores García' : 'Iván Alberto Flores García',
                      'José Foncea Aedo' : 'José Antonio Foncea Aedo',
                      'Arturo Frei Bolívar' : 'Erwin Arturo Frei Bolívar',
                      'Renán Fuentealba Moena' : 'Tulio Renán Fuentealba Moena',
                      'Carlos Garcés Fernández' : 'Carlos Arturo Garcés Fernández',
                      'Víctor González Maertens' : 'Víctor Emerson González Maertens',
                      'Rosa González Román' : 'Rosa Orfilia González Román',
                      'Luis Guastavino Córdova' : 'Luis Alberto Guastavino Córdova', 
                      'Bernardino Guerra Cofré' : 'Bernardino Segundo Guerra Cofré',
                      'Juan Hamilton Depassier' : 'Juan Patricio José Hamilton Depassier',
                      'Marcela Hernando Pérez' : 'Marcela Ximena Hernando Pérez',
                      'Ricardo Hormazábal Sánchez' : 'Luis Ricardo Hormazábal Sánchez', 
                      'Claudio Huepe García' : 'Claudio Humberto Huepe García',
                      'Marta Isasi Barbieri' : 'Marta Eliana Isasi Barbieri',
                      'Tucapel Francisco Jiménez Fuentes' : 'Tucapel Jiménez Fuentes',
                      'Eduardo Koenig Carrillo' : 'Eduardo Octavio Koenig Carrillo',
                      'Jorge Lavandero Illanes' : 'Jorge Exequiel Lavandero Illanes',
                      'Alfredo Lorca Valencia' : 'Alfredo Macario Lorca Valencia',
                      'Luis Maira Aguirre' : 'Luis Osvaldo Maira Aguirre',
                      'María Maluenda Campos' : 'María Adela Maluenda Campos', 
                      'Joel Marambio Páez' : 'Joel Segundo Marambio Páez',
                      'Gladys Marín Millie' : 'Gladys del Carmen Marín Millie',
                      'Juan Buenaventura \(Ventura\) Marín Recabarren' : 'Juan Buenaventura Marín Recabarren',
                      'Luis Martin Mardones' : 'José Luis Martin Mardones', 
                      'Manuel José Matta Aragay' : 'Manuel Matta Aragay',
                      'Patricio Mekis Spikin' : 'Patricio Bryan Mekis Spikin',
                      'Sergio Merino Jarpa' : 'Sergio Ariel Merino Jarpa',                      
                      'Claudia Mix Jiménez' : 'Claudia Nathalie Mix Jiménez',
                      'Hardy Momberg Roa' : 'Hardy René Oscar Momberg Roa',
                      'José Monares Gómez' : 'José Ricardo Monares Gómez',
                      'Julio Montt Momberg' : 'Julio Felipe Montt Momberg',
                      'Ramón Moreno Cruz y Gómez' : 'Ramón Moreno Gómez',
                      'Rafael Moreno Rojas' : 'Rafael Adolfo Moreno Rojas',
                      'José Musalem Saffie' : 'José Plácido Musalem Saffie',   
                      'Manuel J. Navarrete' : 'Manuel Jesús Navarrete T.', 
                      'Emilia Nuyado Ancapichun' : 'Emilia Iris Nuyado Ancapichun',
                      'Hernán Modesto Olave Verdugo' : 'Hernán Olave Verdugo',
                      'Héctor Olivares Solís' : 'Héctor Luis Olivares Solís',                  
                      'Humberto Palza Corvacho' : 'Humberto Manuel Palza Corvacho',
                      'Sergio Pizarro' : 'Sergio Pizarro Mackay',
                      'Blanca Retamal Contreras' : 'Blanca Adelina Retamal Contreras',  
                      'Germán Riesco Zañartu' : 'Germán Miguel Juan Riesco Zañartu',
                      'Mario Ríos Santander' : 'Mario Enrique Ríos Santander',
                      'Hugo Robles Robles' : 'Hugo Orlando Robles Robles',
                      'Ramón H Rojas' : 'Ramón H. Rojas',
                      'Mariano Ruiz-Esquide Jara' : 'Sergio Mariano Ruiz-Esquide Jara',
                      'Wilna Saavedra Cortés' : 'Wilna Yolanda Saavedra Cortés',
                      'Jorge Sabag Villalobos' : 'Jorge Eduardo Sabag Villalobos',
                      'Marisela Santibañez Novoa' : 'Marisela del Carmen Santibañez Novoa',
                      'Camilo Salvo Inostroza' : 'Camilo Armando Salvo Inostroza',
                      'Fernando Sanhueza Herbage' : 'Fernando Humberto Andrés Sanhueza Herbage',
                      'Aníbal Scarella Calandroni' : 'Aníbal Juan Esteban Scarella Calandroni',
                      'Erich Schnake Silva' : 'Alvaro Erich Schnake Silva',
                      'Alejandra Sepúlveda Orbenes' : 'Alejandra Amalia Sepúlveda Orbenes',
                      'Bruno Siebert' : 'Bruno Guillermo Siebert Held',
                      'Vicente Sota Barros' : 'Vicente Agustín de la Sotta Barros', 
                      'Anselmo Sule Candia' : 'Vladimir Anselmo Sule Candia',
                      'Alejandro Toro Herrera' : 'Alejandro Enrique Toro Herrera',
                      'Víctor Torres Jeldes' : 'Víctor Marcelo Torres Jeldes',
                      'Mario Torres Peralta' : 'Mario Julio Torres Peralta',
                      'Ricardo Tudela Barraza' : 'Ricardo Fernando Tudela Barraza',
                      'Pedro Velásquez Seguel' : 'Pedro Antonio Velásquez Seguel',
                      'Mario Venegas Cárdenas' : 'Mario Artidoro Venegas Cárdenas',
                      'Alberto Javier Rafael Zaldívar Larraín' : 'Alberto Zaldívar Larraín',
                      'José Ignacio Zenteno del Pozo y Silva' : 'José Ignacio Zenteno del Pozo',
                      }            
                    
    incongruencias_regex = {'^'+x+'$' : incongruencias[x] for x in incongruencias.keys()}
    candidatos[column] = candidatos[column].replace(incongruencias_regex, regex=True)

    return candidatos

#%%
def nombres_formato_v2(candidatos, column='Candidatos', formato=True):
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
    candidatos : dataframe
        Nombres de candidatos en el nuevo formato.

    """    
    articulos = {'y ':' ',
                 'de la ':'de+la+', 'de los ':'de+los+', 'de las ':'de+las+', 'de ':'de+', 'del ':'del+', 
                 'Las ':'Las+',
                 'San ':'San+', 'Santa ':'Santa+', 
                 'van ':'van+', 'von ':'von+', 
                 'La ':'La+', 'Le ':'Le+',
                 'Da ':'Da+'}            
    articulos_regex = {'\\b'+x : articulos[x] for x in articulos.keys()}    

    apellidos_compuestos2 = {'María y José':'María+y+José',
                             #
                             'Álvarez de Toledo':'Álvarez+de+Toledo',
                             'Barents-von Hohenhagen':'Barents-von+Hohenhagen',                             
                             'Bravo de Naveda':'Bravo+de+Naveda',
                             'Correa de Saa':'Correa+de+Saa',
                             'de Porto Seguro':'de+Porto+Seguro', 'de Vic Tupper':'de+Vic+Tupper', 'Díaz de Valdés':'Díaz+de+Valdés',
                             'García de la Huerta':'García+de+la+Huerta', 'Gayón de Celis':'Gayón+de+Celis', 'Gregorio de las Heras':'Gregorio+de+las+Heras', 'Gutiérrez de Palacios':'Gutiérrez+de+Palacios',
                             'Hurtado de Mendoza':'Hurtado+de+Mendoza',
                             'Ladrón de Guevara':'Ladrón+de+Guevara', 'Lerdo de Tejada':'Lerdo+de+Tejada', 'López de Artigas':'López+de+Artigas',
                             'Manso Velasco':'Manso+de+Velasco', 'Manso de Velasco':'Manso+de+Velasco', 'Márquez de la Plata':'Márquez+de+la+Plata',
                             'Niño de Zepeda':'Niño+de+Zepeda', 
                             'Olaguer Feliú':'Olaguer',
                             'Peña y Lillo':'Peña+y+Lillo', 'Pérez de Arce':'Pérez+de+Arce', 'Pérez de Valenzuela':'Pérez+de+Valenzuela', 'Plaza de los Reyes':'Plaza+de+los+Reyes', 'Ponce de León':'Ponce+de+León',
                             'Ramírez de Arellano':'Ramírez+de+Arellano', 'Ramírez de Saldaña':'Ramírez+de+Saldaña', 'Ruiz de Gamboa':'Ruiz+de+Gamboa',
                             'Sainz de la Peña':'Sainz+de+la+Peña', 'Solo de Zaldívar':'Solo+de+Zaldívar',
                             'de Vic Tupper':'de+Vic+Tupper',
                             'Vásquez de Novoa':'Vásquez+de+Novoa',
                             #
                             # apellidos «antiguos»˙
                             'Álvarez de Bahamonde':'Álvarez+de+Bahamonde',
                             'Bravo de Naveda':'Bravo+de+Naveda', 'Bravo de Saravia':'Bravo+de+Saravia',
                             'Díaz de Saravia':'Díaz+de+Saravia',
                             'Fernández de Braga':'Fernández+de+Braga', 'Fernández de Castro':'Fernández+de+Castro', 'Fernández de Cienfuegos':'Fernández+de+Cienfuegos', 
                             'Fernández de Gandarillas':'Fernández+de+Gandarillas', 'Fernández de Leiva':'Fernández+de+Leiva', 'Fernández de Muras':'Fernández+de+Muras',
                             'Fernández de Palazuelos':'Fernández+de+Palazuelos', 'Fernández de Valdivieso':'Fernández+de+Valdivieso',
                             'López de Linares':'López+de+Linares', 'López de Sotomayor':'López+de+Sotomayor',
                             'Martínez de Aldunate':'Martínez+de+Aldunate', 'Martínez de Luco':'Martínez+de+Luco', 'Martínez de Matta':'Martínez+de+Matta', 'Martínez de Rozas':'Martínez+de+Rozas', 'Martínez de Vergara':'Martínez+de+Vergara',
                             'Montero de Amaya':'Montero+de+Amaya',
                             'Núñez de Guzmán':'Núñez+de+Guzmán', 'Núñez de Silva':'Núñez+de+Silva',
                             'Pérez de Camino':'Pérez+de+Camino', 'Pérez de Carmona':'Pérez+de+Carmona', 'Pérez de Iturrieta':'Pérez+de+Iturrieta', 'Pérez de Ramos':'Pérez+de+Ramos',
                             'Rodríguez de Herrera':'Rodríguez+de+Herrera', 'Ruiz de Azúa':'Ruiz+de+Azúa',
                             'Sáenz de Rozas':'Sáenz+de+Rozas', 'Salvador de Vergara':'Salvador+de+Vergara'
                             }    
    apellidos_compuestos2_regex = {'\\b'+x+'\\b' : apellidos_compuestos2[x] for x in apellidos_compuestos2.keys()}
    
    candidatos[column] = candidatos[column].replace(apellidos_compuestos2_regex, regex=True)    
    candidatos[column] = candidatos[column].replace(articulos_regex, regex=True)

    candidatos[column] = candidatos[column].str.split()                       

    if not formato:
        # se asume que tienen dos apellidos
        candidatos[column] = candidatos[column].map(lambda x: x[2:] +x[0:2] if len(x) > 2 else (x[1]+x[0] if len(x) > 0 else x))
        
    candidatos[column] = candidatos[column].map(lambda x: tuple([u.replace('+',' ') for u in x]))

    return candidatos
