<html>
<head>
<link rel="stylesheet" href="http://cdn.leafletjs.com/leaflet-0.7.2/leaflet.css">
<link rel="stylesheet" href="style.css">
<link href='http://fonts.googleapis.com/css?family=Noto+Sans' rel='stylesheet' type='text/css'>
<title>ALPTRUTh-geo</title>
</head>
<body>
<div id="map" style="height:100%"></div>
<script src="http://cdn.leafletjs.com/leaflet-0.7.2/leaflet.js"></script>
<script src="scripts/leaflet-openweathermap.js"></script>
<script>

var mapquest_att = 'Data, imagery and map information provided by '
			+ '<a href="http://open.mapquest.co.uk" target="_blank">MapQuest</a>, '
			+ '<a href="http://www.openstreetmap.org/" target="_blank">OpenStreetMap</a> and '
			+ '<a href="http://wiki.openstreetmap.org/wiki/Contributors" target="_blank">contributors</a>. '
			+ 'Data: <a href="http://wiki.openstreetmap.org/wiki/Open_Database_License" target="_blank">ODbL</a>, '
			+ 'Map: <a href="http://creativecommons.org/licenses/by-sa/2.0/" target="_blank">CC-BY-SA</a>';

var mapquest_OSM = L.tileLayer ('http://otile{s}.mqcdn.com/tiles/1.0.0/osm/{z}/{x}/{y}.png',
{
	subdomains: '1234',
	attribution: mapquest_att
});


//var topo_hazard_jp = L.imageOverlay ("data/raster/topo_hazard_jp.png", [[39.80109459585579,-105.92225979006423],[39.74961332647341,-105.82125043213578]]).addTo (map).setOpacity(0.5);

//var topo_hazard_lp = L.imageOverlay ("data/raster/topo_hazard_lp.png", [[39.68890969655487,-105.92256669569137],[39.62962529320198,-105.83335661521996]]).addTo (map).setOpacity(0.5);

var wms_server = "/cgi-bin/mapserv.exe?map=../htdocs/alptruth-geo/mapfiles/alptruth-geo.map&"

var topo_hazard = new L.tileLayer.wms (wms_server, 
{
	layers: 'topo-hazard',
	format: 'image/png',
	srs: 'EPSG: 3857',
	transparent: true
});

var stability_hazard = new L.tileLayer.wms (wms_server, 
{
	layers: 'snow-stability',
	format: 'image/png',
	srs: 'EPSG: 3857',
	transparent: true
});

var alptruth_a = new L.tileLayer.wms (wms_server, 
{
	layers: 'alptruth-a',
	format: 'image/png',
	srs: 'EPSG: 3857',
	transparent: true
});
var alptruth = new L.tileLayer.wms (wms_server, 
{
	layers: 'alptruth',
	format: 'image/png',
	srs: 'EPSG: 3857',
	transparent: true
});
var alptruth_l = new L.tileLayer.wms (wms_server, 
{
	layers: 'alptruth-l',
	format: 'image/png',
	srs: 'EPSG: 3857',
	transparent: true
});
var alptruth_p = new L.tileLayer.wms (wms_server, 
{
	layers: 'alptruth-p',
	format: 'image/png',
	srs: 'EPSG: 3857',
	transparent: true
});

var alptruth_t = new L.tileLayer.wms (wms_server, 
{
	layers: 'alptruth-t',
	format: 'image/png',
	srs: 'EPSG: 3857',
	transparent: true
});
var alptruth_r = new L.tileLayer.wms (wms_server, 
{
	layers: 'alptruth-r',
	format: 'image/png',
	srs: 'EPSG: 3857',
	transparent: true
});
var alptruth_u = new L.tileLayer.wms (wms_server, 
{
	layers: 'alptruth-u',
	format: 'image/png',
	srs: 'EPSG: 3857',
	transparent: true
});
var alptruth_th = new L.tileLayer.wms (wms_server, 
{
	layers: 'alptruth-th',
	format: 'image/png',
	srs: 'EPSG: 3857',
	transparent: true
});
var snow_depth = new L.tileLayer.wms (wms_server,
{
	layers: 'snow-depth',
	format: 'image/png',
	srs: 'EPSG: 3857',
	transparent: true
});
var elevation = new L.tileLayer.wms (wms_server,
{
	layers: 'elevation',
	format: 'image/png',
	srs: 'EPSG: 3857',
	transparent: true
});
var slope = new L.tileLayer.wms (wms_server,
{
	layers: 'slope',
	format: 'image/png',
	srs: 'EPSG: 3857',
	transparent: true
});

var clouds = L.OWM.clouds({opacity: 0.8, legendImagePath: 'files/NT2.png'});
var rain = L.OWM.rain({opacity: 0.5});
var snow = L.OWM.snow({opacity: 0.5});
var pressure = L.OWM.pressure({opacity: 0.4});
var pressurecntr = L.OWM.pressureContour({opacity: 0.5});
var temp = L.OWM.temperature({opacity: 0.5});
var wind = L.OWM.wind({opacity: 0.5});

var hazards = 
{
	"ALPTRUTh": alptruth,
	"Topographical": topo_hazard,
	"Snow Stability": stability_hazard,
	"ALPTRUTh: A (Avalanches)": alptruth_a,
	"ALPTRUTh: L (Loading)": alptruth_l,
	"ALPTRUTh: P (Paths)": alptruth_p,
	"ALPTRUTh: T (Terrain Traps)": alptruth_t,
	"ALPTRUTh: R (Rating)": alptruth_r,
	"ALPTRUTh: U (Unstable Snow)": alptruth_u,
	"ALPTRUTh: Th (Thaw Instability)": alptruth_th,
	"Snow Depth": snow_depth,
	"Elevation": elevation,
	"Slope": slope,
	"Clouds": clouds,
	"Rain": rain,
	"Snow": snow,
	"Pressure": pressure,
	"Pressure Contours": pressurecntr,
	"Temperature": temp,
	"Wind": wind
	
};
var base_maps = 
{
	"OSM-MapQuest": mapquest_OSM,
};

var map = L.map('map',
{
	center: [39.7392, -104.9847],
	zoom: 9,
	layers: [mapquest_OSM]
});

var layer_control = L.control.layers(base_maps, hazards).addTo(map);
// patch layer_control to add some titles
var patch = L.DomUtil.create('div', 'owm-layer_control-header');
patch.innerHTML = "<b>Avalanche Hazard</b>"; // 'TileLayers';
layer_control._form.children[2].parentNode.insertBefore(patch, layer_control._form.children[2]);
patch = L.DomUtil.create('div', 'owm-layer_control-header');
patch.innerHTML = "<b>Topography</b>"; // 'Current Weather';
layer_control._form.children[3].children[0].parentNode.insertBefore(patch, layer_control._form.children[3].children[layer_control._form.children[3].children.length-10]);
patch = L.DomUtil.create('div', 'owm-layer_control-header');
patch.innerHTML = "<b>Weather</b>"; // 'Current Weather';
layer_control._form.children[3].children[0].parentNode.insertBefore(patch, layer_control._form.children[3].children[layer_control._form.children[3].children.length-7]);
patch = L.DomUtil.create('div', 'owm-layer_control-header');
patch.innerHTML = "<b>ALPTRUTh Elements</b>"; // 'Current Weather';
layer_control._form.children[3].children[0].parentNode.insertBefore(patch, layer_control._form.children[3].children[layer_control._form.children[3].children.length-19]);
patch = L.DomUtil.create('div', 'leaflet-control-layers-separator');
layer_control._form.children[3].children[0].parentNode.insertBefore(patch, layer_control._form.children[3].children[layer_control._form.children[3].children.length-12]);
patch = L.DomUtil.create('div', 'owm-layer_control-header');
patch.innerHTML = "<b>Base Maps</b>"; // 'Maps';
layer_control._form.children[0].parentNode.insertBefore(patch, layer_control._form.children[0]);

</script>
<!-- <div id="navbuttons"> -->
<!-- <button type="button" class="navbutton"><p class="inner-nav-button">Hybrid<br>ALPTRUTh</p></button><br> -->
<!-- </div> -->
</body>
</html>
