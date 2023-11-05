# congreso-Chile
Módulos en python para generar visualizaciones interactivas de las elecciones de la Cámara de Diputados y el Senado de Chile, desde 1932 en adelante.  

La representación consiste en un mapa elaborado a partir de [Folium](https://python-visualization.github.io/folium/), el cual contiene:
* los resultados de una elección en cada distrito o circunscripción (ordenables gracias a [Tablesorter (Mottie's fork)](https://mottie.github.io/tablesorter/docs/)),
* una leyenda o cuadro lateral, con las votaciones por coalición a nivel territorial y nacional, 
* un diagrama de la composición de la camára respectiva (hecho en [Highcharts](https://www.highcharts.com/)).  

Si bien este repositorio contiene los datos necesarios, es posible generarlos y formatearlos usando los módulos aquí presentes. Los resultados electorales se obtuvieron principalmente mediante web scraping, a través de [beautiful soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/); mientras que los polígonos propios de cada división electoral fueron tratados usando [shapely](https://shapely.readthedocs.io/en/stable/manual.html).

<!--
## Code Example
## Motivation
## Installation
-->

## Uso
Módulos y datos se encuentran en */repo_mapas*, pudiendo ser usados directamente. De momento este proyecto no requiere instalación.  

El script **visualizacion** crea un mapa de una elección *de principio a fin*, vale decir, reuniendo los datos, procesándolos y produciendo una representación en formato html. Los resultados electorales y polígonos de cada división electoral están reunidos en */input*. Las funciones necesarias, ya sea para generar estos datos (en caso de no estar almacenados), consultar informaciones referentes a partidos y coaliciones, además de la creación misma del mapa, están agrupadas en la carpeta */modulos*. Finalmente, en */output* se guardan los distintos mapas generados.

```
├── repo_mapas
│   ├── visualizacion.py
│   ├── modulos
│   ├── input
│   ├── output
```

## Módulos 
<!-- ## API Reference -->

* **division_politica** : entrega la división electoral asociada a cada elección.
* **resultados_elecciones** : extrae, formatea y corrige los resultados electorales. Un conjunto de funciones relacionadas se encuentra en */modulos/resultados*.
* **pactos** : provee informaciones relativas a partidos (siglas, pactos electorales) y leyendas a utilizar en la visualización.
* **mapa_folium** : produce el mapa antes mencionado. En */modulos/mapa* se encuentran las funciones usadas para crear marcadores y popups, cuadro lateral y diagrama de distribución de escaños.

Una descripción más detallada se encuentra en cada archivo.

## Datos
Reunidos en */input*, están organizados de la siguiente manera.

* */parlamentarias* : resultados de cada elección parlamentaria en formato *.csv*. Fueron obtenidos mediante web scraping y diversas fuentes bibliográficas, las cuales pueden ser consultadas [aquí](https://sebastianriffo.github.io/congreso-chile/es/fuentes.html).  

  A nivel de candidatos, la información completa de la elección se tiene desde 1973 en adelante, mientras que entre 1932 y 1969 se dispone de un listado de parlamentarios. Si bien la información del período 1828-1930 se encuentra disponible, tiene carácter preliminar pues aún se encuentra en revisión. 
	    
* */shapes* : shapefiles (*.shp*) de las divisiones político-electorales para cada elección, desde 1989 a la fecha. Aquellos del período 1932-1973 se encuentran en revisión.
  	
  Se consideran las divisiones de **1932**, corregidas para las elecciones de **1941** y **1961** y una nueva versión de **1969**; la usada por el sistema binominal en **1989** y rectificada el **2009**; y finalmente la del sistema proporcional de **2017**, que sufrió algunos cambios en **2021**. Una explicación más detallada de los territorios y sus cambios se encuentra [aquí](https://sebastianriffo.github.io/congreso-chile/es/sistemas.html). 

  * */source* : shapefile con el cual se generaron las divisiones entre 1989 y 2021. 

```
├── repo_mapas
│   ├── input
│   │   ├── parlamentarias
│   │   │   ├── 1828-1891
│   │   │   ├── 1891-1924
│   │   │   ├── 1924-1973
│   │   │   ├── 1973-presente
│   │   ├── shapes
```

Cabe mencionar que los resultados electorales, según el año, se agrupan en los períodos *1828-1891* (repúblicas conservadora y liberal), *1891-1924* (república parlamentaria), *1925-1973* (república presidencial) y *1989-presente* (retorno a la democracia).


<!--
## Tests/Usage
-->

## Resultados
Los mapas generados se encuentran disponibles en el [sitio web de este proyecto](https://sebastianriffo.github.io/congreso-chile/) y en el directorio */output*, cuya organización es similar a la de */input*.  

A modo de ejemplo, las últimas elecciones pueden ser vistas directamente en [diputados 2021](https://sebastianriffo.github.io/congreso-chile/es/mapas/2022-2026_Diputados.html) y [senadores 2021](https://sebastianriffo.github.io/congreso-chile/es/mapas/2022-2026_Senadores.html). 

<!--
## Contributors
-->

## Licencia
[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/deed.en)
