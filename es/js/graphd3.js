/*
D3 SOURCES: 
https://jsfiddle.net/wpc3y1jd/ 
https://observablehq.com/@d3/force-directed-graph/2?intent=fork
https://stackoverflow.com/questions/47544041/how-to-visualize-groups-of-nodes-in-a-d3-force-directed-graph-layout
https://stackoverflow.com/questions/75798624/d3-force-graph-zoom-to-node
form : https://codepen.io/Rastikko/pen/GqNbqM

Js:
- las leyendas podrían estar en otro elemento con fondo blanco
- la paleta de colores es muy corta: esto podría ayudar https://www.sessions.edu/color-calculator/
- vinculos matrimoniales necesitan un marcador distinto

Proyecciones:
- js definirá group en base a los apellidos seleccionados: (d.familia1 in filterGroup) || (d.familia1 not in filterGroup && d.familia2 in filterGroup)
- filter by: gender, eventually multiple positions (congress, ministry, etc)
- personalize popup
- highlight relatives (neighbors)
*/

// CHART DIMENSIONS
const scale = 2;	
const width = scale*800;
const height = scale*600;
const nodeRadius = 5;

// SVG container.
var svg = d3.select("svg")
			.attr("width", width)
			.attr("height", height)
			.attr("viewBox", [0, 0, width, height])
			.attr("style", "max-width: 100%; max-height: 100%;");	

const zoomValue = 1.5; //(filterGroup.length) <= 4 ? 2:1;
const zoomWidth = (width-zoomValue*width)/2;
const zoomHeight = (height-zoomValue*height)/2;

var zoom = d3.zoom().scaleExtent([1, 20])
					.translateExtent([[0, 0], [width, height]])		
					.on("zoom", function () {zoomContainer.attr("transform", d3.event.transform)});

var zoomContainer = svg.call(zoom)
							.call(d3.zoom().transform, d3.zoomIdentity.translate(zoomWidth,zoomHeight).scale(zoomValue))
							.append("g")
							.attr("transform","translate("+zoomWidth+","+zoomHeight+") scale("+zoomValue+")");
// SIMULATION
var simulation = d3.forceSimulation()
					.force("link", d3.forceLink().id(d => d.id).distance(15).strength(
						function(link) {   
							if (link.source.group == link.target.group) {
								return 2; // stronger link for links within a group
							} else {
								return 1; // weaker links for links across groups
							}   
						}) )
					.force("charge", d3.forceManyBody().strength(-75).distanceMax(500))
					.force("center", d3.forceCenter(width / 2, height / 2))
					.force("x", d3.forceX())
					.force("y", d3.forceY())
					.on("tick", ticked);	
// GRAPH
var link = zoomContainer.append("g")
						.attr("class", "links")
						.selectAll("line");						
var node = zoomContainer.append("g")
						.attr("class", "nodes")
						.selectAll("circle");	
						
// arrow definition, source: https://gist.github.com/fancellu/2c782394602a93921faff74e594d1bb1
zoomContainer.append('defs').append('marker')
	.attr('id','arrowhead')
	.attr('viewBox',[0, 0, 10, 10])
	.attr('refX',32)
	.attr('refY',5)
	.attr('orient','auto')
	.attr("markerUnits","strokeWidth")
	.attr('markerWidth',2.5)
	.attr('markerHeight',2.5)
	.append('svg:path')
	.attr("d","M 0 0 L 10 5 L 0 10 z")
	.attr('fill', '#999');
	
// (elements added first to the DOM appear at the back)	
var legendContainer = svg.append('g')
						.attr("class", "legend-graph");
				
	
// GRAPH
function start(dataset, filterGroup, color1checked, color2checked, career) {	
	const color1 = d3.scaleOrdinal().domain(filterGroup).range(color1checked); 
	const color2 = d3.scaleOrdinal().domain(filterGroup).range(color2checked);

//	para definir group: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/assign
//	nodes = data.nodes.filter(function(d) {return filterGroup.indexOf(d.group) != -1}).map(d => Object.assign(d, {group: d.familia1}));
	nodes = dataset.nodes.filter(function(d) {return filterGroup.indexOf(d.group) != -1}).map(d => Object.assign({}, d));

	let names = nodes.map(d => d.id);    
	
	var neighbors = []
	var sources = []
	
	links = dataset.links.filter(function(d) {
									if (names.indexOf(d.source) != -1 && names.indexOf(d.target) != -1) {
										return true
									// parents
									} else if (names.indexOf(d.source) == -1 && names.indexOf(d.target) != -1) {
										neighbors.push(d.source)
									// children 
									} else if (names.indexOf(d.source) != -1 && names.indexOf(d.target) == -1) {
										if (sources.indexOf(d.source) == -1) { neighbors.push(d.target) }
										sources.push(d.source)
									}									
								}).map(d => Object.assign({}, d));

	simulation.nodes(nodes)
	simulation.force("link").links(links);
	simulation.alpha(1).restart().tick();

	link = link.data(links);
    link.exit().remove();
	link = link.enter().append("line")
				.merge(link)
				.attr('stroke', "#999")
				.attr("stroke-opacity",0.6)
				.attr("stroke-width", function(e) { return Math.sqrt(e.value); })
				.attr('marker-end', function(e){if (e.relation == 'ancestry') {
													return 'url(#arrowhead)'
												} else { 
													return 'none' 
												} });
	node = node.data(nodes, d => d.id);
	node.exit().remove();

	node = node.enter()
				.append("circle")
				.attr("class", function(v) {if (v.parlamentario == 1) {
												return "parlamentario"; 
											} else {
												return "otro"; 
											}})
				.classed('node', true) // add «node» to class
				//
				.attr("id", function(v) {return v.id;})
				.attr("r", nodeRadius)
				.attr("fill", function(v) {return nodeColor(v, career, color1, color2); })
				.attr('stroke', "#fff")
				.attr("stroke-width",1)
				.merge(node)
				//
				.on("click", function(v){												
					// zoom +highlight clicked node
					svg.transition().duration(700).call(
						zoom.transform, d3.zoomIdentity.translate((width / 2), (height / 2)).scale(6).translate(-v.x, -v.y),
					);
					
					svg.selectAll('.node.selected')
						.classed('selected', false)
						.style('fill', function(v) {return nodeColor(v, career, color1, color2); });

					d3.select(this)
						.classed('selected', true)
						.style('fill', 'magenta');					

					// left panel
					d3.select(".name")
						.attr("id", v.group)
						.attr("href", v.url).text(v.id);

					if (typeof v.info != 'undefined') { 
						d3.select(".info").text(v.info.replaceAll('),',')\n'));
					} else {
						d3.select(".info").text('');
					}
                })
                .on("mouseover", function(v) {
					d3.select(this).attr("r", 1.25*nodeRadius);
				})  
                .on("mouseout", function(v) {
					d3.select(this).attr("r", nodeRadius);
				}); 

	// leyenda
	legend(filterGroup, color1, career)
	
	// counting neighboring families
	neighbors = [...new Set(neighbors)]

	closestNeighbors = d3.nest().key(d => d.group)
									.rollup(d => d.length).entries(dataset.nodes.filter(d => (neighbors.indexOf(d.id) != -1) && (d.group != 'otros') ))
									.sort(function(a, b){ return d3.descending(a.value, b.value); })
									
	freq = d3.cumsum(d3.nest().key(d => d.value).rollup(d => d.length).entries(closestNeighbors).map(d => d.value)).filter(i => (i <= 10)).slice(-1)[0]
	if (typeof freq != 'undefined') {
		return closestNeighbors.map(d => d.key).slice(0,freq)
	} else { 
		return []
	}
}

function legend(filterGroup, color1, career){
	const congresoCount = d3.rollup(nodes, (D) => D.length, (d) => d.group, (d) => d.parlamentario)

	// legend
	d3.selectAll(".legend-graph > circle.dot").remove();		
	legendContainer.selectAll("mydots").data(filterGroup.map(e => e).sort())	
		.enter().append("circle").attr("class", "dot")
		.attr("cx", scale*10)
		.attr("cy", function(d,i){ return scale*(10 + i*25) })
		.attr("r", scale*nodeRadius)
		.style("fill", function(d){ return color1(d) });

	d3.selectAll(".legend-graph > text.label").remove();	
	legendContainer.selectAll("mylabels").data(filterGroup.map(e => e).sort())
		.enter().append("text").attr("class", "label")
		.attr("x", scale*20)
		.attr("y", function(d,i){return scale*(10 + i*25)}) 
		.style("fill", function(d){ return color1(d) })
		.text(function(d){	if(career.indexOf('parlamentario') != -1){
								return d +' ('+ ((typeof congresoCount.get(d).get(1) != 'undefined') ? congresoCount.get(d).get(1): 0) +')'
							} else {
								return d 
							} })
		.attr("text-anchor", "left")
		.style("font-size", 16*scale+"px")
		.style("alignment-baseline", "middle");
}

// BUNCH OF FUNCTIONS
// boundaries
function checkBounds(d){
	if (d.x < nodeRadius) d.x = nodeRadius;
	if (d.x > width-nodeRadius) d.x = width -nodeRadius;
	if (d.y < nodeRadius) d.y = nodeRadius;
	if (d.y > height-nodeRadius) d.y = height -nodeRadius;
}

// Set the position attributes of links and nodes each time the simulation ticks.
function ticked() {
	link.attr("x1", function(d) { checkBounds(d.source); return d.source.x; })
		.attr("y1", function(d) { checkBounds(d.source); return d.source.y; })
		.attr("x2", function(d) { checkBounds(d.target); return d.target.x; })
		.attr("y2", function(d) { checkBounds(d.target); return d.target.y; });

	node.attr("cx", function(d) { checkBounds(d); return d.x; })
		.attr("cy", function(d) { checkBounds(d); return d.y; })
	// drag behavior.    
		.call(d3.drag()
		.on("start", dragstarted)
		.on("drag", dragged)
		.on("end", dragended));
	}
// Reheat the simulation when drag starts, and fix the subject position.
function dragstarted(d) {
	if (!d3.event.active) simulation.alphaTarget(0.3).restart();
	d.fx = d.x;
	d.fy = d.y;
}
// Update the subject (dragged node) position during drag.
function dragged(d) {
	d.fx = d3.event.x;
	d.fy = d3.event.y;
}	
// Restore the target alpha so the simulation cools after dragging ends.
// Unfix the subject position now that it’s no longer being dragged.
function dragended(d) {
	if (!d3.event.active) simulation.alphaTarget(0);
	d.fx = null;
	d.fy = null;
}  
	
// COLORING
// palette
function coloring(){
	//tableau20
	const color = [	"#1f77b4", "#aec7e8", //azul
					"#ff7f0e", "#ffbb78", //naranjo
					"#2ca02c", "#98df8a", //verde
					"#d62728", "#ff9896", //rojo
					"#9467bd", "#c5b0d5", //morado
					"#8c564b", "#c49c94", //café
					"#e377c2", "#f7b6d2", //rosado
					"#7f7f7f", "#c7c7c7", //gris
					"#bcbd22", "#dbdb8d", //verde oliva
					"#17becf", "#9edae5"  //cyan 
					]
	
	const DC = color.filter(function(element, index, array) { return (index % 2 == 0);});
	const LC = color.filter(function(element, index, array) { return (index % 2 == 1);});
	
	return [DC,LC]
}	

function updateFamiliesColors(families, color1checked, color2checked, filterGroup, DC, LC) {			
	if (filterGroup.length > families.length) {
		families.push(filterGroup.filter(d => families.indexOf(d) == -1)[0])

		color1checked.push(popColor(color1checked, DC));								
		color2checked.push(popColor(color2checked, LC));

	} else {			
		var index = []
		families = families.filter(function(d) {
										if (filterGroup.indexOf(d) != -1) {
											index.push(families.indexOf(d));
											return true;
										} else {
											return false;
											} })

		color1checked = index.map(i => color1checked[i]);
		color2checked = index.map(i => color2checked[i]);
	}
	
	return [families, color1checked, color2checked]
}

function nodeColor(v, career, color1, color2) {
	if(v.parlamentario == 1 || career.indexOf('parlamentario') == -1) {
		return color1(v.group); 
	} else {
		return color2(v.group); 
	}
}


// FREQUENCIES
// source: https://dev.to/perelynsama/getting-the-frequency-of-an-element-in-an-array-in-javascript-lgf
function popColor(color1checked, DC){
	const count1 = {};
	color1checked.forEach(e => count1[e] ? count1[e]++ : count1[e] = 1 );

	if (Object.keys(count1).length < DC.length){
		return DC.filter(d => Object.keys(count1).indexOf(d) == -1)[0]
	} else {
		return Object.keys(count1).find(key => count1[key] == Math.min.apply(Math, Object.values(count1)) )
	}
}

// sugerir familias: quienes tienen mas miembros en el congreso	
function totalCount(dataset){
	var congresoCount = d3.rollup(dataset.nodes.map(d => Object.assign({}, d)), (D) => D.length, (d) => d.group, (d) => d.parlamentario);

	var u = []
	for (var key of congresoCount.keys()){
		if (congresoCount.get(key).get(1) >= 0){
			u.push({key : key, value: congresoCount.get(key).get(1)})
		}
	}
	u.sort(function(a, b){ return d3.descending(a.value, b.value); }) 

	freq = d3.cumsum(d3.nest().key(d => d.value).rollup(d => d.length).entries(u).map(d => d.value)).filter(i => (i <= 10)).slice(-1)[0]				
	closestNeighbors = u.map(d => d.key).slice(0,freq)

	return closestNeighbors
}


// RENDERING
// get data
var dataset;
d3.json("networkdata.json", function(data) {
	dataset = data;

	// group categories and colors
	var keys = d3.values(d3.groups(dataset.nodes, d => d.group)).map(function(x) {return x[0];}).sort();
	const [DC, LC] = coloring()

	var families = ['Errázuriz', 'Larraín', 'Valdés', 'Vicuña'];
	var color1checked = DC.slice(0, families.length);
	var color2checked = LC.slice(0, families.length);	

	// individuals
	var names = d3.values(d3.groups(dataset.nodes, d => d.id)).map(function(x) {return x[0];}).sort();
	var names_selected = []

	// render
	closestNeighbors = start(dataset, families, color1checked, color2checked, ['parlamentario']);
	
	// checkboxes (right)
	familist(keys, families)
	selected(families.slice())
	suggestions(closestNeighbors)
	
	namelist(names, families)
				
	largestFamilies = totalCount(dataset)

	d3.select('#families').selectAll('.category').on('change', function() {
		var filterGroup = d3.select('#families').selectAll('.category:checked').nodes().map(box => box.id);
		var filterCareer = d3.select('#positions').selectAll('.category:checked').nodes().map(box => box.id);
		
		// update parameters
		[families, color1checked, color2checked] = updateFamiliesColors(families, color1checked, color2checked, filterGroup, DC, LC);
		
		closestNeighbors = start(dataset, families, color1checked, color2checked, filterCareer);		
				
		// update info (left)
		if (families.indexOf(d3.select(".name").attr("id")) == -1){
			d3.select(".name").attr("id", '').attr("href", '').text('');
			d3.select(".info").text('');
		}
		
		// update checkboxes (right)
		selected(families.slice())		

		d3.select('#fam-suggestions').selectAll('.checkbox').remove();			
		if(families.length > 0){
			suggestions(closestNeighbors)
		}
		else {					
			suggestions(largestFamilies)			
		}
	})

	d3.select('#fam-selections').selectAll('.category').on('change', function() {
		var filterSwitch = d3.select('#fam-selections').selectAll('.category:checked').nodes().map(box => box.id);
		var filterCareer = d3.select('#positions').selectAll('.category:checked').nodes().map(box => box.id);
				
		filterGroup = []
		families = [] 
		color1checked = [] 
		color2checked = []

		start(dataset, families, color1checked, color2checked, filterCareer);	
		
		// info (left)
		d3.select(".name").attr("id", '').attr("href", '').text('');
		d3.select(".info").text('');
		
		// checkboxes (right)
		d3.select('#families').selectAll('.category:checked').property('checked', false);	
		
		d3.select('#fam-selections').selectAll('label').select('#Deseleccionar\\ todo').property('checked', false);	
		selected([])					
		
		d3.select('#fam-suggestions').selectAll('.checkbox').remove();	
		suggestions(largestFamilies)		
	});	
	
	
	d3.select('#positions').selectAll('.category').on('change', function() {
		const color1 = d3.scaleOrdinal().domain(families).range(color1checked); 
		const color2 = d3.scaleOrdinal().domain(families).range(color2checked);
		
		var filterCareer = d3.select('#positions').selectAll('.category:checked').nodes().map(box => box.id);
		
		if (filterCareer.indexOf('parlamentario') != -1) {
			d3.selectAll(".otro").attr("fill", d => color2(d.group));
		} else {
			d3.selectAll(".otro").attr("fill", d => color1(d.group));
		}
		legend(families, color1, filterCareer)
		
	});

	d3.select('#individuals').selectAll('.category').on('change', function() {
		const color1 = d3.scaleOrdinal().domain(families).range(color1checked); 
		const color2 = d3.scaleOrdinal().domain(families).range(color2checked);


		var filterGroup = d3.select('#individuals').selectAll('.category:checked').nodes().map(box => box.id);
		
		// highlight clicked node
		// de momento: entre las familias presentes		
		// mas adelante: si no esta disponible, desplegar su familia
		
		// career is not defined
		career = ['parlamentario']
		
		svg.selectAll('.node.selected')
			.classed('selected', false)
			.style('fill', function(v) {return nodeColor(v, career, color1, color2); });

		const id = ('circle#'+d3.select(this).attr('id')).replaceAll(' ','\\ ').replace('(','\\(').replace(')','\\)')

		svg.selectAll(id)
			.classed('selected', true)
			.style('fill', 'magenta')
			.filter(function(v){ 
				svg.transition().duration(700).call(
					zoom.transform, d3.zoomIdentity.translate((width / 2), (height / 2)).scale(6).translate(-v.x, -v.y),
				);
					
				//left panel
				d3.select(".name")
					.attr("id", v.group)
					.attr("href", v.url).text(v.id)
					
				if (typeof v.info != 'undefined') { 
					d3.select(".info").text(v.info.replaceAll('),',')\n'));
				} else {
					d3.select(".info").text('');
				}
			});
		
		// de momento: solo identifica en base a un click
		d3.select('#individuals').selectAll('.category:checked').property('checked', false);	
	})	
})

// CHECKBOXES
// see https://stackoverflow.com/questions/10771505/appending-multiple-elements-in-d3
function familist(keys, families){
	d3.select('#families').selectAll('.checkbox')		
		.data(keys)
		.enter()
		.append('div')
		.attr('class', 'checkbox')
		.append('label').attr('id', id => id).html(function(id) {
													if (families.indexOf(id) != -1) {
														var checkbox = '<input id="' + id + '" type="checkbox" class="category" checked>';
													} else {
														var checkbox = '<input id="' + id + '" type="checkbox" class="category">';
													}	
													return checkbox +' '+id;});	
}

function selected(switchKeys){
	if (switchKeys.indexOf('Deseleccionar todo') == -1){
		switchKeys.unshift(['Deseleccionar todo'])
	}
	
	var a = d3.select('#fam-selections').selectAll('.checkbox').data(switchKeys, function(id) {return id} )
						
	a.enter()
		.append('div')
		.attr('class', 'checkbox')
		.append('label').attr('id', id => id).html(function(id) {
													if (id != 'Deseleccionar todo') {
														var checkbox = '<input id="' + id + '" type="checkbox" class="category" checked>';
													} else {
														var checkbox = '<input id="' + id + '" type="checkbox" class="category">';
													}	
													return checkbox +' '+id;})
		.on('click', function() {
			const id = ('#'+d3.select(this).attr('id')).replaceAll(' ','\\ ').replace('(','\\(').replace(')','\\)').replace(',','\\,');
			d3.select('#families').selectAll('label').select(id).property('checked', false);
			
			if (id != '#Deseleccionar\\ todo'){
				d3.select('#families').selectAll('label').select(id).on('change')();
			}
		});

	a.exit().remove();	
}

function suggestions(closestNeighbors){
	d3.select('#fam-suggestions').selectAll('.checkbox')
		.data(closestNeighbors)
		.enter()
		.append('div')
		.attr('class', 'checkbox')
		.append('label').attr('id', id => id)
		.html(function(id) {return '<input id="' + id + '" type="checkbox" class="category">'+' '+id;})
		.on('click', function() {
			const id = ('#'+d3.select(this).attr('id')).replaceAll(' ','\\ ').replace('(','\\(').replace(')','\\)').replace(',','\\,');
			
			d3.select('#families').selectAll('label').select(id).property('checked', true);		
			// fire click on its twin element: 
			// https://stackoverflow.com/questions/32610092/why-isnt-the-checkbox-change-event-triggered-when-i-do-it-programatically-in-d3
			d3.select('#families').selectAll('label').select(id).on('change')();
		});
}

function namelist(keys, families){
	d3.select('#individuals').selectAll('.checkbox')		
		.data(keys)
		.enter()
		.append('div')
		.attr('class', 'checkbox')
		.append('label').attr('id', id => id).html(function(id) {
													var checkbox = '<input id="' + id + '" type="checkbox" class="category">';
														
													return checkbox +' '+id;});	}
