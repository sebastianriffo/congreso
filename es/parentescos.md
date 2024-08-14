---
layout: dashboard

title: Parentescos

lang: es
ref: kinship

published: True
order: 3

excerpt_separator: <!--more-->

customjs:
- http://d3js.org/d3.v4.min.js
- https://d3js.org/d3-array.v2.min.js
- https://d3js.org/d3-scale-chromatic.v1.min.js
---

<div class="container">
<div class="row-about">	
	<div class="col" style="min-height:500px;">
        <div class="panel" style="width:300px; height:calc(85vh - 50px);"> 

		<div>
		<form role="form" class="cat" id="positions">
			<legend><b>Carrera política</b></legend>
		        <div class="checkbox">
		        <label for="parlamentario">  <input id="parlamentario" type="checkbox" class="category" checked> </label> Parlamentario/a
			</div>
		</form>
		</div>		
		<hr style="background-color:#7f7f7f; margin:12px 0px 12px 0px;">

		<div>
			<legend><b>Informaciones</b></legend>		
			<div><a class="name" target="_blank"></a></div>
			<div class="info" style="font-size:12px; white-space: pre-wrap; overflow-y:auto;"></div>
		</div>

	</div>	
	</div>	

	<div class="col" style="width:100%; height:calc(85vh - 50px); min-height:500px; padding:0px 10px 0px 10px;">
		<svg id="tree"></svg>
	</div>
	
	<div class="col" style="min-height:500px;">				
		<div class="tab">
			<button class="tablinks" onclick="openCity(event, 'familias')">Familias</button>
			<button class="tablinks" onclick="openCity(event, 'individuos')">Personas</button>
		</div>

		<div id="familias" class="panel tabcontent" style="width:250px; height:calc(85vh - 94px); display:flex; flex-direction: column;">
			<input class="input" type="text" placeholder="Buscar apellido" id="fam-search" style="max-width:100%; box-sizing: border-box; margin:0px 0px 8px 0px;"/>

			<div style="max-height:90px; overflow-y:auto;">
			<form role="form" class="cat" id="families">
			</form>
			</div>		
			<hr style="background-color:#7f7f7f; margin:12px 0px 12px 0px;">

			<legend><b>Selección</b></legend>		
			<div style="max-height:140px; overflow-y:auto;">
			<form role="form" class="cat" id="fam-selections">						
			</form>
			</div>
			<hr style="background-color:#7f7f7f; margin:12px 0px 12px 0px;">

			<legend><b>Sugerencias</b></legend>		
			<div style=" overflow-y:auto;">
			<form role="form" class="cat" id="fam-suggestions">
			</form>
			</div>									
		</div>	
		
		<div id="individuos" class="panel tabcontent" style="width:250px; height:calc(85vh - 94px); display:none; flex-direction: column;">
			<input class="input" type="text" placeholder="Buscar parlamentario/a" id="ind-search" style="max-width:100%; height: 30px; box-sizing: border-box; margin:0px 0px 8px 0px;"/>

			<div style="overflow-y:auto;">
			<form role="form" class="cat" id="individuals">
			</form>
			</div>		
			
			<!--
			<hr style="background-color:#7f7f7f; margin:12px 0px 12px 0px;">

			<legend><b>Selección</b></legend>		
			<div style="max-height:140px; overflow-y:auto;">
			<form role="form" class="cat" id="fam-selections">	
			</form>
			-->
			
		</div>
		
	</div>	
</div>
</div>

<div style="color:#525252; font-size:12px;">
<!--
<h3> Precisiones </h3>
-->

<p>
<h4 style="margin:0px"> Base de datos </h4>
Última revisión: 31 de mayo de 2024. Elaboración propia a partir del artículo <a href="https://link.springer.com/article/10.1007/s11186-022-09491-3" target="_blank"> The structure of political conflict (...)</a>, de Naim Bro; reseñas biográficas de la <a href="https://www.bcn.cl/historiapolitica/resenas_parlamentarias/" target="_blank">Biblioteca del Congreso Nacional de Chile</a> e informaciones provenientes de <a href="https://www.genealog.cl" target="_blank">genealog.cl</a>, <a href="https://anales.cl/" target="_blank">anales.cl</a>, entre otros.
</p>

<!--
<p>
<h4 style="margin:0px"> Familias </h4>
Se consideran 150 apellidos
</p>

<p>
<h4 style="margin:0px"> Metodología </h4>
</p>
-->

</div>

<script src="js/graphd3.js"></script>

<script>
document.addEventListener("DOMContentLoaded", function(event) { 

	setTimeout(function(){
	const search = document.getElementById("fam-search");
	const labels = document.querySelector("#families").querySelectorAll(".checkbox > label");
		
	const removeAccents = str =>
	  str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');

	search.addEventListener("input", () => Array.from(labels).forEach((element) => element.style.display = removeAccents(element.childNodes[0].id.toLowerCase()).includes(removeAccents(search.value.toLowerCase())) ? "inline" : "none"))
	}, 250);
	
	setTimeout(function(){
	const search = document.getElementById("ind-search");
	const labels = document.querySelector("#individuals").querySelectorAll(".checkbox > label");
		
	const removeAccents = str =>
	  str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');

	search.addEventListener("input", () => Array.from(labels).forEach((element) => element.style.display = removeAccents(element.childNodes[0].id.toLowerCase()).includes(removeAccents(search.value.toLowerCase())) ? "inline" : "none"))
	}, 250);	
})

function openCity(evt, cityName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById(cityName).style.display = "flex";
  evt.currentTarget.className += " active";
}
</script>

<style type="text/css">
.container {
	margin-top: 30px; padding: 10px 0px 0px 0px;
}

.panel {
	background-color: #eaecef;
	padding:15px;
}

.tab {
	overflow: hidden;
	border: 1px solid #ccc;
	background-color: #f1f1f1;
}
.tab button {
	background-color: inherit;
	float: left;
	border: none;
	outline: none;
	cursor: pointer;
	padding: 12px 12px;
	transition: 0.3s;
	font-size:16px;
}
.tab button:hover {
	background-color: #ddd;
}

</style>
