# congreso-Chile
Módulos en python para generar visualizaciones interactivas de las elecciones de la Cámara de Diputados y el Senado de Chile, desde 1932 en adelante.

La visualización consiste en un mapa elaborado en [folium](https://python-visualization.github.io/folium/), el cual contiene 
* los resultados de una elección por distrito o circunscripción (ordenables gracias a [tablesorter](https://mottie.github.io/tablesorter/docs/)),
* una leyenda o cuadro con las votaciones por coalición a nivel territorial y nacional, 
* un diagrama de la composición de la camára respectiva (hecho en [Highcharts](https://www.highcharts.com/)).  

Los resultados electorales se obtuvieron principalmente por web scraping, a través de [beautiful soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/); mientras que los polígonos fueron tratados usando [shapely](https://shapely.readthedocs.io/en/stable/manual.html).

A continuación, una breve descripción de los módulos y datos disponibles, presentes en **/repo_mapas**.

## Módulos
Agrupados en la carpeta **/modulos**, entregan los resultados electorales y la división electoral de cada elección. Su finalidad es la siguiente.
* *division_politica.py* : genera los polígonos de distritos o circunscripciones.
* *resultados_elecciones.py* : extrae, formatea y corrige los resultados electorales. Un conjunto de scripts asociados se encuentra en **/modulos/resultados**.
* *pactos.py* : grupo de funciones referentes a siglas de partidos, pactos electorales y leyendas a utilizar en la visualización.
* *mapa_folium.py* : genera el mapa antes mencionado.
  Una descripción más detallada se encuentra en cada archivo.

Por último, el script *visualizaciones.py* crea uno o más mapas, buscando o generando los polígonos y datos de una elección parlamentaria, según sea el caso. Por medio del módulo *mapa_folium* los produce y guarda en formato *.html*.   

## Datos
Los resultados electorales y polígonos de cada división político-electoral están reunidos en **/input**, organizados por
* **/parlamentarias** : resultados de cada elección parlamentaria en formato *.csv*. Fueron obtenidos mediante web scraping y diversas fuentes bibliográficas, las cuales pueden ser consultadas [aquí]((https://sebastianriffo.github.io/congreso-chile/es/fuentes.html).  

  A nivel de candidatos, la información completa de la elección se tiene desde 1973 en adelante, mientras que entre 1932 y 1969 se dispone de un listado de parlamentarios. La información del período 1828-1930 es preliminar, pues aún se encuentra en revisión. Una explicación más detallada se encuentra [aquí]((https://sebastianriffo.github.io/congreso-chile/es/datos.html).  
	    
* **/shapes** : shapefiles (*.shp*) de las divisiones político-electorales para cada elección, desde 1989 a la fecha. Aquellos del período 1932-1973 se encuentran en revisión.
  	
  Se consideran las divisiones de **1932**, corregidas para las elecciones de **1941** y **1961** y una nueva versión de **1969**; la usada por el sistema binominal en **1989** y rectificada el **2009**; y finalmente la del sistema proporcional de **2017**, que sufrió algunos cambios en **2021**. Una explicación más detallada de los territorios y sus cambios se encuentra [aquí](/sistemas.html). 

  * **/source** : shapefile con el cual se generaron las divisiones entre 1989 y 2021. 

Según corresponda, las carpetas por año están agrupadas en los períodos **1828-1891** (repúblicas conservadora y liberal), **1891-1924** (república parlamentaria), **1925-1973** (república presidencial) y **1989-presente** (retorno a la democracia).

## Resultados
Los mapas generados se encuentran disponibles en el [sitio web de este proyecto](https://sebastianriffo.github.io/congreso-chile/) y en el directorio **/output**. A modo de ejemplo, las últimas elecciones pueden ser vistas directamente en [diputados 2021](https://sebastianriffo.github.io/congreso-chile/es/mapas/2022-2026_Diputados.html) y [senadores 2021](https://sebastianriffo.github.io/congreso-chile/es/mapas/2022-2026_Senadores.html). 



