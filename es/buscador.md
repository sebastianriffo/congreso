---
layout: default

title: Buscador

lang: es
ref: search

published: True
order: 2

excerpt_separator: <!--more-->

customjs:
- https://code.jquery.com/jquery-3.7.0.js
- https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js
- https://cdn.datatables.net/plug-ins/1.13.7/filtering/type-based/accent-neutralise.js

customcss:
- https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css
---


<div class="display">
  <table id="example" style="width:100%;">
      <thead>
          <tr>
              <th scope="col">Parlamentario (1828-2024)</th>
              <th scope="col">Partido</th>
              <th scope="col">Partido_completo</th>              
              <th scope="col">Trayectoria</th>
          </tr>
      </thead>
  </table>
</div>

<div style="color:#525252; font-size:12px;">
<h3> Precisiones </h3>

<p>
<h4 style="margin:0px"> Apellidos </h4>
Se utilizó un orden paterno-materno, aún cuando este fue instaurado oficialmente en 1885. Las partículas &laquo;de&raquo; e &laquo;y&raquo; propias del siglo XIX fueron suprimidas, excepto en aquellos que las portan en la actualidad (por ejemplo, <i>de Toro</i>). Los apellidos compuestos llevan guión, salvo <i>Santa Cruz</i>, <i>Santa María</i> y aquellos con &laquo;de&raquo; o similares, como <i>Pérez de Arce</i>, <i>Plaza de los Reyes</i>, entre otros. 
</p>

<p>
<h4 style="margin:0px"> Cargos </h4>
Hasta 1891 se utilizó el título de <u>propietario</u> para Diputados y Senadores, quienes en caso de ausencia eran reemplazados por un <u>suplente</u>, categoría escogida conjuntamente en cada elección. Al quedar vacante una senaturía, se elegía a un <u>subrogante</u> al inicio de la siguiente legislatura, para así completar el período senatorial. Estos mecanismos de sustitución serían simplificados con la elección de un <u>reemplazante</u>, quién asume el resto del período por cese del mandato del titular. Si hoy en día es nombrado por el partido del parlamentario renunciado, hasta 1973 lo era mediante elecciones complementarias. La noción de <u>presuntivo</u> se refiere a quienes en principio fueron electos, siendo este resultado desestimado por el Congreso. Finalmente, entre 1990 y 2006 existieron los Senadores <u>designados</u>.
</p>

<p>
<h4 style="margin:0px"> Períodos parlamentarios </h4>
Corresponden a la duración completa, aún si el parlamentario no cumplió con su totalidad, ya sea por motivos propios o cierre del Congreso (lo cual ha ocurrido en tres ocasiones: 1924, 1932 y 1973). En el caso de los Senadores reemplazantes (o subrogantes) se considera todo el período si ingresaron en la primera parte, y la mitad o tercios correspondientes en caso contrario.
</p>

<p>
<h4 style="margin:0px"> Base de datos </h4>
Última revisión: 31 de mayo de 2024. Falta verificar y completar las militancias entre 1828 y 1930.
</p>
</div>

<!-- fuente: https://live.datatables.net/jorexujo/678/edit -->
<script type="text/javascript" class="init">
/*
arreglar output de ciertas búsquedas: 
demócrata: PD en vez de PDC/UDI/etc
*/
$(document).ready( function () {
var table = $('#example').DataTable({
	language: {
	        url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/es-CL.json',
	},
	ajax: {
	        url: 'https://raw.githubusercontent.com/sebastianriffo/congreso-chile/main/repo_mapas/input/parlamentarias/bcn_database.json',
        	type: 'GET',
        	dataType: 'json',
	        dataSrc:"",
      	},
	processing: true,
	serverSide: false,   

	lengthMenu: [ [5,10, 25, 50, 100, -1], [5, 10, 25, 50, 100, "All"] ],	
	pageLength: 5,
	searching: true,
	paging: true,
	deferRender: true,
	scrollCollapse: true,
	scroller: true,
                    	
      	columns: [
           { data: 'Parlamentario',
		render: function ( data, type, row) {
			if (row.url !== null){
				link = '<a href='+row.url+' target="_blank">'+data+'</a>';
			} 
			else {link = data;}
			return link;
		}
           },                    
           
           { data: 'Partido'},
           
           { data: 'Partido_completo',
           	visible: false,
           	searchable: true,
           },
                      
           { data: 'Trayectoria',
           	render: function ( data, type, row) {
           		data = data.toString().replace(/\),/g, ') <br>');
           		return data;
           	}
           	
           },
           ]
      	});
      	
$('.dataTables_filter input').off().on('keyup', function() {
	var input = this.value.trim()

	/*
	Unión: también entrega UDI, USRACh, UCCP, etc.
	if(input == 'unión'){
		input = 'La Unión'
		$('#example').DataTable().search('\\b' + input + '\\b', true, false).draw();	
	}
	
	Demócrata: además de PD, entrega PDC, UDI, PRSD
	else if(input == 'demócrata'){
		input = 'Partido Demócrata'
		$('#example').DataTable().search('\\b' + input + '\\b', true, false).draw();	        	
        }
        
        Socialista: adems USOPO
        
        radical: ademas DR
        
        Independiente: IND y además, UDI, API, PRI, etc
        
        Nacional: partido nacional, está el monttvarista (y PN-A) y el de los 60
        entrega el MNI también, UNI, RN, falange nacional, PADENA, etc,         
        Balmacedista: PLDe
        Ibañista
                
	else{
		$('#example').DataTable().search('\\b' + input + '\\b', true, true).draw();
	}      
	console.log(input);  
	*/
	
	$('#example').DataTable().search('\\b' + input + '\\b', true, true).draw();
	});    

});      	
</script>

<!--

-->

