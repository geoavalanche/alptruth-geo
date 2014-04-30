alptruth-geo
==

Geospatial model / application of ALPTRUTh model, thesis by Thomas Horner (2014).
Look for the upcoming Geospatial / GIS scientific journal manuscript on the use and technology.
Developed entirely with FOSS4G.  Load SEXTANTE models into QGIS Processing plugin to use.

Developed for/using the following data sources:

| Data Requirement | Data Source for Colorado, USA | Data Preparation |
-------------------|-------------------------------|-------------------------|
| DEM |  NAIP 10m | (Optional) Tile to manageable sizes for analysis, (Required) Reproject to a projected coordinate system
Biomass | USDA Biomass | (Optional) Resample to DEM resolution, (Optional) Clip to DEM analysis regions, (Required) Reproject to a projected coordinate system
Snowdata | NSIDC SNODAS | (Required) Remove all "Created by: " information from .hdr files
Bulletin/Observations | Scraping of CAIC website (avalanche.state.co.us) | (Required) Working internet connection, (Required) PHP and server application running, (Required) Vector of forecast regions with matching IDs


##Requirements


| Software | Plug-Ins / Addons |
|----------|---------|
| QGIS 2.2 | Processing (SEXTANTE) |
| PCRaster 4.0.1 | Python 2.7 & NumPy 1.8 |
| PHP 5 | simple_dom_scraper.php |
| Web Server (Apache) | PHP, MapServer CGI |
| PostgreSQL | PostGIS |
| MapServer | WMS |

##Setting Up the Model

If you are using NSIDC SNODAS data, GDAL/OGR cannot handle the large strings in the .hdr files.  This is due to the information in the "Created XXXXX" descriptors which are unnecessary for proper use of the data.  If you need to remove this information from a large number of .hdr files, you can use a batch grep utility like TextCrawler (Windows) to replace 'Created.*' with '' (nothing).  Then you can run the included batch script (convert\_snodas\_data) without issue.

##Running the Model


1) Configure the webserver and PostGIS database and ensure the scraping scripts work and the database is accessible.

2) Allow QGIS to look for experimental plugins, then add the 'Processing' plug-in to QGIS.

2) Prepare data sets before the first run by using the batch snowdata conversion tool and using the "Model Setup" models in the QGIS Processing toolbox.  After all data sets have been prepared, the model can be run entirely automated, save for the manual downloading of new snowcover datasets.

2) Run the full model from the QGIS Toolbox or using a python script with the inputs prepared.

3) Ensure the output of the model is in the data directory for the webmap or into a PostGIS database.

4) If you want, set up a batch script to automatically download the latest snow data and run the model daily.
