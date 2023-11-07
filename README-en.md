---
layout: default

title: readme

lang: en
ref: readme

published: true
order: 7
---

# congreso-Chile
[![en](https://img.shields.io/badge/lang-es-blueviolet.svg)](https://github.com/sebastianriffo/congreso-chile/blob/main/README.md)

Python modules for creating interactive visualizations of Chilean parliamentary elections from 1932 onwards, covering both the Chamber of Deputies and the Senate.  

Build on [Folium](https://python-visualization.github.io/folium/), these maps include the following key features:

* a detailed display of constituency results, sortable thanks to [Tablesorter (Mottie's fork)](https://mottie.github.io/tablesorter/docs/).
* A side panel presenting local and national results obtained by the main alliances.
* An apportionment diagram revealing the composition of a chamber, with seats color-coded by alliances, which was produced on [Highcharts](https://www.highcharts.com/).  

Although this repository contains all the necessary data, you can also generate and format it by using the modules provided here. Electoral data has been obtained through web scraping, using [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/); whereas the constituencies' shapes have been constructed with help of [Shapely](https://shapely.readthedocs.io/en/stable/manual.html).

<!--
## Code Example
## Motivation
## Installation
-->

## Usage
The Modules and data are stored in */repo_mapas* and can be used directly. Currently, this project does not require any installation.

The script **visualizacion** creates an election map *from scratch*. This involves collecting and processing data, to then generate a representation in HTML format. Electoral data and constituencies' shapes can be found in */input*. Modules to generate this data (if it's not available), retrieve information from parties and alliances, and construct the aforementioned map are placed in */modulos*, see Modules](#modules) below. Finally, the resulting maps are stored in */output*.

```
├── repo_mapas
│   ├── visualizacion.py
│   ├── modulos
│   ├── input
│   ├── output
```

## Modules
<!-- ## API Reference -->
* **division_politica** : yields the constituencies' shapes for each election.
* **resultados_elecciones** : extracts, formats, and corrects electoral data. Other auxiliary functions can be found in */modulos/resultados*.
* **pactos** : provides information regarding parties (acronyms, alliances) and leyends to be used in the visualization.
* **mapa_folium** : produces the map. Several functions, located in */modulos/mapa*, are responsible for creating markers and popups, a side panel and an apportionment diagram. 

A more detailed description of each module can be found in their respective files.

## Data
Stored in */input*, it is organized as follows.

* */parlamentarias* : this directory contains electoral results in CSV format,  obtained through web scraping and from multiple sources, which can be further explored [here](https://sebastianriffo.github.io/congreso-chile/en/sources.html).  

  Election results at the constituency-level are available from 1973 onwards, although for the period 1932-1969, a parliamentary list is provided. Information concerning the years 1828-1930 is also accesible, yet several details require validation.

* */shapes* : includes constituencies' shapefiles used for each election from 1989 to present. Those from 1932-1973 are still under review.
  
  The constituencies used in **1932** are considered, with adjustments made in **1941** and **1961**, followed by a new version from **1969**. It also includes the electoral districts utilized from **1989** and amended in **2009**, when the binomial voting was in place. Finally, with the implementation of the proportional representation system, a new division was introduced in **2017** and later rectified in **2021**.
 
   A more detailed explanation of these changes can be found [here](https://sebastianriffo.github.io/congreso-chile/es/sistemas.html) (however, it is available only in spanish).

  * */source* : it contains the shapefile used to generate the divisions between 1989 and 2021. 

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

It should be noted that electoral data is grouped into the following periods: *1828-1891* (conservative and liberal republics), *1891-1924* (parlamentary republic), *1925-1973* (presidential republic) y *1989-presente* (so-called transition to democracy).


<!--
## Tests/Usage
-->

## Results
Maps produced are available at this [project website](https://sebastianriffo.github.io/congreso-chile/) and in the */output* folder, which has a similar structure to */input*.  

For example, you can directly view the most recent elections under [deputies 2021](https://sebastianriffo.github.io/congreso-chile/es/mapas/2022-2026_Diputados.html) and [senators 2021](https://sebastianriffo.github.io/congreso-chile/es/mapas/2022-2026_Senadores.html). 

<!--
## Contributors
-->

## License
[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/deed.en)

