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
<script>
var mapquest_OSM = L.tileLayer ('http://otile{s}.mqcdn.com/tiles/1.0.0/osm/{z}/{x}/{y}.png',
{
	subdomains: '1234',
	attribution: 'Map data ' + L.TileLayer.OSM_ATTR
});


//var topo_hazard_jp = L.imageOverlay ("data/raster/topo_hazard_jp.png", [[39.80109459585579,-105.92225979006423],[39.74961332647341,-105.82125043213578]]).addTo (map).setOpacity(0.5);

//var topo_hazard_lp = L.imageOverlay ("data/raster/topo_hazard_lp.png", [[39.68890969655487,-105.92256669569137],[39.62962529320198,-105.83335661521996]]).addTo (map).setOpacity(0.5);

var wms_server = "/cgi-bin/mapserv.exe?map=../htdocs/alptruth-geo/mapfiles/alptruth-geo.map&"

var topo_hazard = new L.tileLayer.wms (wms_server, 
{
	layers: 'topo-hazard',
	format: 'image/png',
	srs: 'EPSG: 900913',
	transparent: true
});

var hazards = 
{
	"Hazard: <b>Topographical</b>": topo_hazard
};
var base_maps = 
{
	"Base: <b>OSM-MapQuest</b>": mapquest_OSM
};

/*
var alptruth_elements =
{
	"ALPTRUTh: A (Avalanches)": false,
	"ALPTRUTh: L (Loading)": false,
	"ALPTRUTh: P (Paths)": false,
	"ALPTRUTh: T (Terrain Traps)": false,
	"ALPTRUTh: R (Rating)": false,
	"ALPTRUTh: U (Unstable Snow)": false,
	"ALPTRUTh: Th (Thaw Instability)": false
};
*/

var map = L.map('map',
{
	center: [39.7392, -104.9847],
	zoom: 9,
	layers: [mapquest_OSM, topo_hazard]
});

L.control.layers (base_maps, hazards).addTo (map);

</script>
<!-- <div id="navbuttons"> -->
<!-- <button type="button" class="navbutton"><p class="inner-nav-button">Hybrid<br>ALPTRUTh</p></button><br> -->
<!-- </div> -->
</body>
</html>