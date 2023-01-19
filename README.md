# congreso-Chile
Módulos en python para generar visualizaciones interactivas de las elecciones de la Cámara de Diputados y el Senado de Chile, desde 1941 en adelante.

La visualización consiste en un mapa elaborado en [folium](https://python-visualization.github.io/folium/), el cual contiene 
* los resultados de una elección por distrito o circunscripción (ordenables gracias a [tablesorter](https://mottie.github.io/tablesorter/docs/)),
* una leyenda o cuadro con las votaciones por coalición a nivel territorial y nacional, 
* un diagrama de la composición de la camára respectiva (hecho en [Highcharts](https://www.highcharts.com/)).  

Los resultados electorales se obtuvieron principalmente por web scraping, a través de [beautiful soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/); mientras que los polígonos fueron tratados usando [shapely](https://shapely.readthedocs.io/en/stable/manual.html).

A continuación, una breve descripción de los datos y módulos, disponibles en **/repo_mapas**.

## Datos
Los resultados electorales y polígonos de cada división político-electoral están reunidos en **/input**, organizados por
* **/parlamentarias** : resultados de cada elección parlamentaria en formato *.csv*. Fueron obtenidos mediante web scraping y diversas fuentes bibliográficas, las cuales pueden ser consultadas [aquí](/fuentes.html).  
	
  A nivel de candidatos, el detalle de la elección se tiene desde 1973, mientras que entre 1941 y 1969 solo se extrajo un listado de parlamentarios. Los datos incluyen distrito o circunscripción, coalición, partido y nombre; votación y porcentaje (a partir de 1973), y una columna que indica si fueron electos; además de una última columna con un link a la biografía parlamentaria de la BCN, en caso de haber integrado la cámara en dicha elección.  
  
  Los resultados por partidos y coaliciones están disponibles para 1945 y desde 1961 en adelante. Notar que en el caso del Senado, los datos fueron levantados a partir de 1989. 
  
* **/shapes** : shapefiles (*.shp*) de las divisiones político-electorales para cada elección, desde 1989 a la fecha. Aquellos del período 1941-1973 se encuentran en revisión.
  	
  Se consideran las divisiones de **1941**, corregidas para la elección **1961** y una nueva versión de **1969**; la usada por el sistema binominal en **1989** y rectificada el **2009**; y finalmente la del sistema proporcional de **2017**, que sufrió algunos cambios en **2021**. Una explicación más detallada de los territorios y sus cambios se encuentra [aquí](/sistemas.html). 
  * **/source** : shapefile con el cual se generaron las divisiones entre 1989 y 2021. 

En ambos casos, las carpetas por año están agrupadas según los períodos **1925-1973** (república presidencial) y **1989-presente** (retorno a la democracia).

## Módulos
Agrupados en **/modulos**, estos se exponen según su finalidad. La siguiente es una descripción general, pues una más detallada se encuentra en cada archivo.

### Mapas
* *mapa_folium.py* : genera el mapa antes mencionado.
* *pactos.py* : funciones referentes a siglas de partidos, pactos electorales y leyendas a utilizar.

### Datos
Los resultados de cada elección y sus polígonos asociados fueron generados mediante
* *division_politica.py* : entrega los polígonos de distritos o circunscripciones entre 1989 y 2021.
* *resultados_elecciones.py* : extrae, formatea y corrige los resultados electorales.
* *resultados_miscelaneo.py* : funciones para formatear nombres y extraer biografías parlamentarias de la BCN.

Por último, el script *visualizaciones.py* crea uno o más mapas, buscando los polígonos y datos de una elección parlamentaria (o generándolos en caso contrario). Por medio del módulo *mapa_folium* los produce y guarda en formato *.html*.   

## Resultados
Los mapas generados se encuentran disponibles en el [sitio web de este proyecto](/index.html) y en el directorio **/output**. A modo de ejemplo, las últimas elecciones pueden ser vistas directamente en [diputados 2021](mapas/2022-2026_Diputados.html) y [senadores 2021](mapas/2022-2026_Senadores.html). 



