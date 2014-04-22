#
#  alptruth-geo
#  ALPTRUTh - 'U' Unstable Snow Model
#  Requires PCRaster and Python2.7
#  This script should be obtained from
#  http://github.com/thurs/alptruth-geo/
#
#  @version v1-beta1 
#  @author Thomas Horner
#  @contact thomas.horner@ucdenver.edu
#  @website thurs.github.io
#  @date 4/21/2014
#  @license MIT
#
from pcraster import *
from pcraster.framework import *
from array import array
import time
import sys
from datetime import date, timedelta

# timesteps is defined in command-line. future: have a default
timesteps = int(sys.argv[1]);


class SnowStabilityModel(DynamicModel):
	def __init__(self, cloneMap):
		DynamicModel.__init__(self)
		setclone(cloneMap)
		
	def initial (self):
		# Build the filename string -- Masked daily FTP tars NSIDC SNODAS
		# rr_mmmffppppSvvvvTttttooooTSyyyymmddhhIPOOO.xxx.gz
		self.iter = 0;
		self.snowfall_layers = list()
		self.rainfall_layers = list()
		self.snow_depths = list()
		self.snow_temps = list()
		self.snow_sublimations = list()
		self.snow_melts = list()
		self.snow_mm = list()
		self.snow_layers = list()
		self.blowing_snows = list ()
		self.dhp = scalar (-1) # Depth hoar problem indicator
		self.rrfp = scalar (0) # Radiation recrystallization facet problem
		self.rrfp_depth = scalar (0) # Radiation recrystallization facet problem depth check
		self.mlrfp = scalar (0) # Melt-layer recrystallization facet problem
		self.mlrfp_depth = scalar (0) # Melt-layer recrystallization facet problem depth check
		self.wsp = scalar (0) # Wet slab problem
		self.melt_days = scalar (0) # Consecutive days of melting
		self.stable_factor = scalar (0) # "Stability" factor that increases with time and favorable conditions
		self.non_precip_days = scalar (0) # Consecutive days without any precipitation
		
		self.load_status = 0;
		self.STARTING_DATE = time.strptime ('20131101' , '%Y%m%d')
		#self.month_lengths = array ("i", [31,28,31,30,31,30,31,31,30,31,30,31])
		# constants in the filename shared by all input data
		self.dtf_rrmmm = "us_ssm"
		self.dtf_oooo = "TTNA"

		# Precipitation (snow)
		self.dtf_ff = "v0"
		self.dtf_ppppS = "1025S"
		self.dtf_vvvv = "lL01"
		self.dtf_Ttttt = "T0024"
		self.dtf_TS = "TS" #yyyymmdd "05"
		self.dtf_I = "D"
		self.dtf_POOO = "P001"

		print "Loading all snow precipitation event rasters..."
		#load all snowfall
		for self.x in range (0, timesteps):
			self.current_date = date (self.STARTING_DATE.tm_year, self.STARTING_DATE.tm_mon, self.STARTING_DATE.tm_mday) + timedelta(self.x)
			self.file_name = self.dtf_rrmmm + self.dtf_ff + self.dtf_ppppS + self.dtf_vvvv + self.dtf_Ttttt + self.dtf_oooo + self.dtf_TS + self.current_date.strftime ('%Y%m%d') + "05" + self.dtf_I + self.dtf_POOO
			self.snowfall_layers.append(self.readmap ("snowdata/" + self.file_name))
			print ".",
			self.load_status += 1
			report (self.snowfall_layers [self.x] , "output/" + generateNameT("snowfall", self.x))
		print "Complete."	
		
		# Precipitation (non-snow)
		self.dtf_ff = "v0"
		self.dtf_ppppS = "1025S"
		self.dtf_vvvv = "lL00"
		self.dtf_Ttttt = "T0024"
		self.dtf_TS = "TS" #yyyymmdd "05"
		self.dtf_I = "D"
		self.dtf_POOO = "P001"

		print "Loading all non-snow precipitation event rasters..."
		#load all non-snow fall
		for self.x in range (0, timesteps):
			self.current_date = date (self.STARTING_DATE.tm_year, self.STARTING_DATE.tm_mon, self.STARTING_DATE.tm_mday) + timedelta(self.x)
			self.file_name = self.dtf_rrmmm + self.dtf_ff + self.dtf_ppppS + self.dtf_vvvv + self.dtf_Ttttt + self.dtf_oooo + self.dtf_TS + self.current_date.strftime ('%Y%m%d') + "05" + self.dtf_I + self.dtf_POOO
			self.rainfall_layers.append(self.readmap ("snowdata/" + self.file_name))
			print ".",
			self.load_status += 1
			report (self.rainfall_layers [self.x] , "output/" + generateNameT("rainfall", self.x))
		print "Complete."	
		
		
		# Snow depth -- correlate this with the mass of falling snow to determine density and depth
		self.dtf_ff = "v1"
		self.dtf_ppppS = "1036tS"
		self.dtf_vvvv = "__"
		self.dtf_Ttttt = "T0001"
		self.dtf_TS = "TS" #yyyymmdd "05"
		self.dtf_I = "H"
		self.dtf_POOO = "P001"
		
		print "Loading all snow depth rasters..."
		for self.x in range (0, timesteps):
			self.current_date = date (self.STARTING_DATE.tm_year, self.STARTING_DATE.tm_mon, self.STARTING_DATE.tm_mday) + timedelta(self.x)
			self.file_name = self.dtf_rrmmm + self.dtf_ff + self.dtf_ppppS + self.dtf_vvvv + self.dtf_Ttttt + self.dtf_oooo + self.dtf_TS + self.current_date.strftime ('%Y%m%d') + "05" + self.dtf_I + self.dtf_POOO
			self.snow_depths.append(self.readmap ("snowdata/" + self.file_name) / scalar(1000))
			print ".",
			report (self.snow_depths [self.x] , "output/" + generateNameT("depth", self.x))
		print "Complete."
		

		print "Translating snow events into thickness..."
		#translate snowfall into mm
		for self.x in range (0, timesteps):
			if self.x < 1:
				self.snow_mm.append(self.snow_depths[self.x])
			else:
				self.snow_mm.append(max(scalar(0),self.snow_depths[self.x] - self.snow_depths[self.x - 1]))
			
			#report (self.snow_mm [self.x] > scalar(10), "output/" + generateNameT("layers", self.x))
			report (self.snow_mm [self.x] , "output/" + generateNameT("snowmm", self.x))
			print ".",
		print "Complete."	
		
		
		# Snow temperature - used for determining stability changes
		self.dtf_ff = "v1"
		self.dtf_ppppS = "1038wS"
		self.dtf_vvvv = "__"
		self.dtf_Ttttt = "A0024"
		self.dtf_TS = "TS" #yyyymmdd "05"
		self.dtf_I = "D"
		self.dtf_POOO = "P001"
		
		print "Loading all snow temperature rasters..."
		for self.x in range (0, timesteps):
			self.current_date = date (self.STARTING_DATE.tm_year, self.STARTING_DATE.tm_mon, self.STARTING_DATE.tm_mday) + timedelta(self.x)
			self.file_name = self.dtf_rrmmm + self.dtf_ff + self.dtf_ppppS + self.dtf_vvvv + self.dtf_Ttttt + self.dtf_oooo + self.dtf_TS + self.current_date.strftime ('%Y%m%d') + "05" + self.dtf_I + self.dtf_POOO
			self.snow_temps.append(self.readmap ("snowdata/" + self.file_name) - scalar (273))
			print ".",
			report (self.snow_temps [self.x], "output/" + generateNameT("temp", self.x))
		print "Complete."	
		
		
		#sublimation
		self.dtf_ff = "v1"
		self.dtf_ppppS = "1050"
		self.dtf_vvvv = "lL00"
		self.dtf_Ttttt = "T0024"
		self.dtf_TS = "TS" #yyyymmdd "05"
		self.dtf_I = "D"
		self.dtf_POOO = "P000"
		
		print "Loading all sublimation rasters..."
		for self.x in range (0, timesteps):
			self.current_date = date (self.STARTING_DATE.tm_year, self.STARTING_DATE.tm_mon, self.STARTING_DATE.tm_mday) + timedelta(self.x)
			self.file_name = self.dtf_rrmmm + self.dtf_ff + self.dtf_ppppS + self.dtf_vvvv + self.dtf_Ttttt + self.dtf_oooo + self.dtf_TS + self.current_date.strftime ('%Y%m%d') + "05" + self.dtf_I + self.dtf_POOO
			self.snow_sublimations.append(self.readmap ("snowdata/" + self.file_name) - scalar (273))
			print ".",
			report (self.snow_sublimations [self.x], "output/" + generateNameT("subl", self.x))
		print "Complete."	
		
		
		#melt
		self.dtf_ff = "v1"
		self.dtf_ppppS = "1044"
		self.dtf_vvvv = "bS__"
		self.dtf_Ttttt = "T0024"
		self.dtf_TS = "TS" #yyyymmdd "05"
		self.dtf_I = "D"
		self.dtf_POOO = "P000"
		
		print "Loading all snowmelt rasters..."
		for self.x in range (0, timesteps):
			self.current_date = date (self.STARTING_DATE.tm_year, self.STARTING_DATE.tm_mon, self.STARTING_DATE.tm_mday) + timedelta(self.x)
			self.file_name = self.dtf_rrmmm + self.dtf_ff + self.dtf_ppppS + self.dtf_vvvv + self.dtf_Ttttt + self.dtf_oooo + self.dtf_TS + self.current_date.strftime ('%Y%m%d') + "05" + self.dtf_I + self.dtf_POOO
			self.snow_melts.append(self.readmap ("snowdata/" + self.file_name))
			print ".",
			report (self.snow_melts [self.x], "output/" + generateNameT("melt", self.x))
		print "Complete."	
		
		#blowing snow sublimation
		self.dtf_ff = "v1"
		self.dtf_ppppS = "1039"
		self.dtf_vvvv = "lL00"
		self.dtf_Ttttt = "T0024"
		self.dtf_TS = "TS" #yyyymmdd "05"
		self.dtf_I = "D"
		self.dtf_POOO = "P000"
		
		print "Loading all blowing snow sublimation rasters..."
		for self.x in range (0, timesteps):
			self.current_date = date (self.STARTING_DATE.tm_year, self.STARTING_DATE.tm_mon, self.STARTING_DATE.tm_mday) + timedelta(self.x)
			self.file_name = self.dtf_rrmmm + self.dtf_ff + self.dtf_ppppS + self.dtf_vvvv + self.dtf_Ttttt + self.dtf_oooo + self.dtf_TS + self.current_date.strftime ('%Y%m%d') + "05" + self.dtf_I + self.dtf_POOO
			self.blowing_snows.append(self.readmap ("snowdata/" + self.file_name))
			print ".",
			report (self.blowing_snows [self.x], "output/" + generateNameT("blowsnow", self.x))
		print "Complete."
		
		print "Running dynamic model..."
		
	def dynamic (self):

		self.temperature = self.readmap ("output/temp")
		self.snowmm = self.readmap ("output/snowmm")
		self.rainfall = self.readmap ("output/rainfall")
		self.melt = self.readmap ("output/melt")
		self.subl = self.readmap("output/subl")
		self.blowingsnow = self.readmap ("output/blowsnow")
		self.snow_depth = self.readmap ("output/depth")
		
		self.melt_days = cover(ifthenelse (self.melt == scalar (0), scalar(0), self.melt_days + scalar(1)),scalar(0))
		self.non_precip_days = cover(ifthenelse (pcrand(self.snowmm == scalar(0), self.rainfall == scalar(0)), self.non_precip_days + scalar(1), scalar(0)),scalar(0))
		
		self.stable_factor = cover(ifthenelse ( pcrand(pcrand (self.non_precip_days > scalar(5), self.subl > scalar(-500)), self.blowingsnow > scalar(-300)), self.stable_factor + scalar(1), scalar(0)) , scalar (0))
		self.mlrfp = ifthenelse ( pcror(self.stable_factor > scalar(0), pcrand((self.blowingsnow / scalar(-100000)) > self.mlrfp_depth, self.mlrfp_depth < scalar(0.001))), scalar (0), self.mlrfp)
		self.rrfp = ifthenelse ( pcror(self.stable_factor > scalar (2), pcrand((self.blowingsnow / scalar(-100000)) > self.rrfp_depth, self.rrfp_depth < scalar(0.001))), scalar (0), self.rrfp)
		self.wsp = ifthenelse (pcror(self.melt_days > scalar(1), self.rainfall > scalar(0)), scalar(1), scalar(0))
		
		# Calculates formation of facets by radiation recrystallization
		self.rrfp = cover(max(self.rrfp,ifthenelse ( pcrand (self.subl < scalar(-500), self.melt < scalar(0)), scalar (1), scalar (0))),scalar(0))
		self.rrfp_depth = cover(self.rrfp * (self.rrfp_depth + self.snowmm), scalar(0))
		self.rrfp = cover(ifthenelse (self.rrfp_depth > scalar(1), scalar(0), self.rrfp),scalar(0))
		self.rrfp_depth = cover(self.rrfp_depth * self.rrfp, scalar(0))
		
		self.mlrfp = cover(max(self.mlrfp,ifthenelse ( pcrand  (pcror( pcror (self.subl < scalar(-500), self.melt > scalar(0)), self.rainfall > scalar(0)), (self.snowmm > scalar(0))), scalar (1), scalar (0))),scalar(0))
		self.mlrfp_depth = cover(self.mlrfp * (self.mlrfp_depth + self.snowmm), scalar(0))
		self.mlrfp = cover(ifthenelse (self.mlrfp_depth > scalar(1), scalar(0), self.mlrfp),scalar(0))
		self.mlrfp_depth = cover(self.mlrfp_depth * self.mlrfp, scalar(0))
		
		self.temp_min = (scalar (0) - self.temperature) * scalar(2) #assumes average snowpack temperature is the median and constructs a low temperature value
		self.temperature_gradient = scalar(self.temp_min / self.snow_depth);
		self.temperature_gradient_exceeded = ifthenelse(self.temperature_gradient > scalar(10), scalar (1), scalar (-1)) #Temperature gradient is > 1C / cm
		self.dhp = scalar(self.dhp) + scalar(self.temperature_gradient_exceeded)
		self.dhp = ifthenelse (scalar(self.dhp) < scalar(-5), scalar(5), scalar(self.dhp))
		self.dhp = cover(ifthenelse (self.dhp > scalar(30), scalar(30), scalar(self.dhp)),scalar(-1))
		
		# Reset all stability indicators to 0 if no snow cover
		self.mlrfp = ifthenelse (self.snow_depth > scalar(0), self.mlrfp, scalar(0))
		self.rrfp = ifthenelse (self.snow_depth > scalar(0), self.rrfp, scalar(0))
		self.wspp = ifthenelse (self.snow_depth > scalar(0), self.rrfp, scalar(0))
		self.dhp = ifthenelse (self.snow_depth > scalar(0), self.dhp, scalar(0))
		self.stable_factor = ifthenelse (self.snow_depth > scalar(0), self.stable_factor, scalar(0))	
		
		report (self.dhp, "output/" + generateNameT("dpthhoar", self.currentTimeStep()))
		report (self.wsp, "output/" + generateNameT("wetslab", self.currentTimeStep()))
		report (self.mlrfp, "output/" + generateNameT("mlrfprob", self.currentTimeStep()))
		report (self.rrfp, "output/" + generateNameT("rrfprob", self.currentTimeStep()))
		
		self.unstable_snow = max(ifthenelse (pcrand(self.dhp > scalar (0), self.snow_depth < scalar (1)), scalar(1), scalar (0)) + scalar(self.rrfp_depth > 0.01) + scalar(self.mlrfp) - scalar (self.stable_factor > scalar(0)) + scalar(self.wsp), scalar(0))
		report (self.unstable_snow, "output/" + generateNameT("unstable", self.currentTimeStep()))
	

ssModel = SnowStabilityModel("clone_co.map")
dynSSModel = DynamicFramework (ssModel, timesteps-1)
dynSSModel.run()
