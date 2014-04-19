for /r %%g in (*.hdr) do gdal_translate -ot Float32 -of PCRaster -mo PCRASTER_VALUESCALE=VS_SCALAR "%%g" "%%~dpng.map"
rem You can use the -projwin argument to clip the result to the area in question.  For Colorado, -projwin -110 41 -102 37
