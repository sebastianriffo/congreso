---
layout: default

title: Visualizaciones parlamentarias

lang: es
ref: home

published: true
order: 1
---

Una representación interactiva de la composición de la Cámara de Diputados y el Senado de Chile, desde las elecciones de 1932 en adelante. Inspirado en lo hecho por [DecideChile](https://2021.decidechile.cl/#/ev/2021.nov/ct/2021.nov.D/){:target="_blank"}, [SERVEL](https://www.servel.cl/centro-de-datos/resultados-electorales-historicos-gw3/){:target="_blank"} y [Wikipedia](https://es.wikipedia.org/wiki/Elecciones_parlamentarias_de_Chile_de_2021){:target="_blank"}, estos mapas fueron elaborados a partir de Python (folium, beautiful soup, pandas), QGIS y Highcharts, integrando diversas fuentes.

La información de cada elección se presenta en tres niveles: 

<div class="row">
  <div class="column">
    <a href="https://sebastianriffo.github.io/congreso-chile/es/mapas/2022-2026_Diputados.html"><img src="../fig/home-1.png"></a>
    <div class="text"> 
    <h4> Resultados individuales </h4> 
    Cada ícono representa el número de parlamentarios a elegir en el territorio respectivo. De estar disponibles, se presentan los resultados detallados, pudiendo ser ordenados y filtrados según quienes fueron electos. </div>
  </div>
  <div class="column">
    <a href="https://sebastianriffo.github.io/congreso-chile/es/mapas/2022-2026_Diputados.html"><img src="../fig/home-2.png"></a>
    <div class="text"> 
    <h4> Resultados por territorio electoral </h4> 
    Al interactuar con un distrito o circunscripción, se muestra la votación obtenida por las principales coaliciones, y en caso contrario, sus resultados a nivel nacional. </div>
  </div>
  <div class="column">
    <a href="https://sebastianriffo.github.io/congreso-chile/es/mapas/2022-2026_Diputados.html"><img src="../fig/home-3.png"></a>
    <div class="text"> 
    <h4> Distribución de escaños </h4>
    La composición de la cámara en cuestión se expone en un diagrama, cuyos escaños están coloreados por coalición y agrupados por partidos. Estos últimos contienen el listado de sus parlamentarios. </div>
  </div>
</div>

