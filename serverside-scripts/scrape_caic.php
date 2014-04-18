<?
/*	CAIC Scraper .php - Thomas Horner, 2014
	Avalanche Hazard Model Project, University of Colorado Denver
	@author Thomas Horner <thomas.horner@ucdenver.edu>
	
	(IDs from the CAIC Site as of March 2014:)
	0 - Steamboat
	1 - Front Range
	2 - Vail and Summit County
	3 - Sawatch
	4 - Aspen
	5 - Gunnison
	6 - Grand Mesa
	7 - North San Juans
	8 - South San Juans
	9 - Sangre de Cristo
	
	Classifies danger as either 1 or 0 for a hazard raster of CAIC forecast polys.  
	If danger is larger than (2) Moderate, 1 is written, if not, 0.  
	Uses a simple flatfile with values separated by newlines.
	Flatfile is parsed by QGIS/SEXTANTE python field calculator model element for final model.
*/

//Small PHP library for parsing HTML DOM
require ('simple_html_dom.php');
//Final array of danger ratings to be written to the flatfile
$danger = array ();
for ($i = 0; $i < 10; $i ++)
{
	$html = file_get_html('http://avalanche.state.co.us/caic/pub_bc_avo.php?zone_id=' . $i);
	$first = 0;
	$danger_ind = 0;
	$danger_scrape = 0;
	$cur_danger = 0;
	foreach($html->find('strong') as $element) 
	{
		$danger_str = $element->innertext . '<br>';
		$cur_danger = filter_var($danger_str, FILTER_SANITIZE_NUMBER_INT);
		if ($cur_danger > $danger_scrape)
		{
			$danger_scrape = $cur_danger;
		}
	}
	if ($danger_scrape > 2)
	{
		$danger_ind = 1;
	}
	$danger[$i] = $danger_ind . "\n";
	//echo $danger_ind;
}
$danger[10] = "Do not delete - flatfile CAIC data for realtime avalanche modelling.\nContact Thomas Horner, <thomas.horner@ucdenver.edu>\n";
$danger[11] = "Generated " . date('Y-m-d');
file_put_contents("caic_zones_danger.txt", $danger);
?>