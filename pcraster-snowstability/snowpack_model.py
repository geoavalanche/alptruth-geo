#
#  alptruth-geo
#  ALPTRUTh - 'U' Unstable Snow Model
#  Requires PCRaster and Python2.7
#  This script should be obtained from
#  http://github.com/thurs/alptruth-geo/
#
#  @version v1-beta3 
#  @author Thomas Horner
#  @contact thomas.horner@ucdenver.edu
#  @website thurs.github.io
#  @date 4/23/2014
#  @license MIT
#

# PCRaster framework and libraries
from pcraster import *
from pcraster.framework import *

# Additional requirements for the python script
from array import array
import time
import sys
import os
from datetime import date, timedelta
import argparse

# timesteps is defined in command-line. future: have a default
timesteps = int(sys.argv[1])


class SnowStabilityModel(DynamicModel):

	# This model is a PCRaster DynamicModel
	def __init__(self, cloneMap):
		DynamicModel.__init__(self)
		setclone(cloneMap)									# PCRaster requires a clonemap that sets the extents and cellsize
	
	# Initialization
	def initial (self):
		
		# -- Initialize raster maps for the model --
		self.snow_depths = list ()							# List of snow depth rasters
		self.snow_temps = list ()							# List of snow temperature rasters
		self.snow_sublimations = list ()					# List of snow sublimation rasters
		self.snow_melts = list ()							# List of snow melt rasters
		self.snow_m = list ()								# List of snow event rasters (m)						
		self.blowing_snows = list ()						# List of blowing snow rasters
		self.rainfall_layers = list ()						# List of rainfall rasters
		
		# -- Initialize model parameters for determining snow stability, TODO: can be set via command line --
		self.start_date = '20131101'						# Starting date: In YYYYMMDD
		self.time_increment = 24							# TODO: Time increment in hours between each time step
		self.bridging_depth = scalar (0.75)					# Bridging depth: How much snow must accumulate above a weak layer to prevent energy from propagating down and releasing the slab
		self.temp_gradient_tg = scalar (10) 				# Temperature gradient (K/m) required for TG metamorphism (hoar formation)
		self.temp_gradient_et = scalar (5)					# Temperature gradient (K/m) required for ET metamorphism (stabilization)
		self.stabilizer_nonprecip_days = 3					# Stabilizing factor: Days without precipitation
		self.stabilizer_nonprecip_amt = scalar (0.05)		# Stabilizing factor: Maximum increase in snow depth to be considered a non-precipitation day	
		self.stabilizer_min_blowing_snow = scalar (-300)	# Stabilizing factor: Minimum blowing snow sublimation
		self.dhp_minimum = scalar (-7)						# Depth hoar: Minimum value for the problem indicator (would represent significant stabilization)
		self.dhp_maximum = scalar (30)						# Depth hoar: Maximum value for the problem indicator (maximum number of days it would require to stabilize a persistent depth hoar problem)
		self.dhp_mf = scalar (3)							# TODO: self.dhp_mf: snowpack temperature decreases dhp based on inverse depth (self.dhp_mf - (1+temp)/depth)
		self.dhp_trigger_threshold = scalar (5)				# Depth hoar indicator value to flag the instability raster
		self.rrfp_max_sublimation = scalar (-500)			# Radiant recrystallization: Max value to represent the minimum amount of solar insolation for this problem to be triggered
		self.wet_slab_melt_days = scalar (3)				# Wet slab: minimum number of melt days to cause a wet slab problem
		self.mlrfp_stabilization_days = scalar (1)			# Days where stable_factor > 1 to remove melt layer recrystallization instability
		self.rrfp_stabilization_days = scalar (3)			# Days where stable_factor > 1 to remove radiant recrystallization instability
		self.weak_layer_burial_depth = scalar (0.01)		# Minimum depth a weak layer/instability must be buried to trigger a problem
		
		# -- Initialize indicator raster maps for the model --
		self.dhp_indicator_r = scalar (-1) 					# Depth hoar problem indicator
		self.rrfp = scalar (0) 								# Radiation recrystallization facet problem
		self.rrfp_depth = scalar (0)						# Radiation recrystallization facet problem depth check
		self.mlrfp = scalar (0) 							# Melt-layer recrystallization facet problem
		self.mlrfp_depth = scalar (0) 						# Melt-layer recrystallization facet problem depth check
		self.wsp = scalar (0) 								# Wet slab problem
		self.melt_days = scalar (0) 						# Consecutive days of melting
		self.stable_factor = scalar (0) 					# "Stability" factor that increases with time and favorable conditions
		self.non_precip_days = scalar (0) 					# Consecutive days without any precipitation
		
		self.STARTING_DATE = time.strptime (self.start_date , '%Y%m%d')
		
		# 	Build the filename string -- Designed for use with NSIDC SNODAS masked daily tars (FTP)
		#	
		#	SNODAS file name format:
		# 	rr_mmmffppppSvvvvTttttooooTSyyyymmddhhIPOOO.map
		#
		
		# constants in the filename shared by all input data
		self.dtf_rrmmm = "us_ssm"
		self.dtf_oooo = "TTNA"
		
		# -- Load Precipitation (non-snow) Rasters --
		self.dtf_ff = "v0"
		self.dtf_ppppS = "1025S"
		self.dtf_vvvv = "lL00"
		self.dtf_Ttttt = "T0024"
		self.dtf_TS = "TS"
		self.dtf_I = "D"
		self.dtf_POOO = "P001"

		os.system('cls' if os.name == 'nt' else 'clear')
		print "     Snowpack Stability Model for ALPTRUTh-geo (python/PCRaster)"
		print "                     v1-beta3  5/4/2014"
		print "\n\n    (1 / 8) Loading all non-snow precipitation event rasters\n"
		
		# Load all liquid precipitation events
		for self.x in range (0, timesteps):
			self.current_date = date (self.STARTING_DATE.tm_year, self.STARTING_DATE.tm_mon, self.STARTING_DATE.tm_mday) + timedelta(self.x)
			self.file_name = self.dtf_rrmmm + self.dtf_ff + self.dtf_ppppS + self.dtf_vvvv + self.dtf_Ttttt + self.dtf_oooo + self.dtf_TS + self.current_date.strftime ('%Y%m%d') + "05" + self.dtf_I + self.dtf_POOO
			self.rainfall_layers.append(self.readmap ("snowdata/" + self.file_name))
			print "-",
			report (self.rainfall_layers [self.x] , "output/" + generateNameT("rainfall", self.x))
		print "Complete."	
		
		# -- Load Snow Depth Rasters --
		self.dtf_ff = "v1"
		self.dtf_ppppS = "1036tS"
		self.dtf_vvvv = "__"
		self.dtf_Ttttt = "T0001"
		self.dtf_TS = "TS" #yyyymmdd "05"
		self.dtf_I = "H"
		self.dtf_POOO = "P001"
		
		os.system('cls' if os.name == 'nt' else 'clear')
		print "\n\n    (2 / 8) Loading all snow depth rasters\n"
		
		for self.x in range (0, timesteps):
			self.current_date = date (self.STARTING_DATE.tm_year, self.STARTING_DATE.tm_mon, self.STARTING_DATE.tm_mday) + timedelta(self.x)
			self.file_name = self.dtf_rrmmm + self.dtf_ff + self.dtf_ppppS + self.dtf_vvvv + self.dtf_Ttttt + self.dtf_oooo + self.dtf_TS + self.current_date.strftime ('%Y%m%d') + "05" + self.dtf_I + self.dtf_POOO
			self.snow_depths.append(self.readmap ("snowdata/" + self.file_name) / scalar(1000))
			print "-",
			report (self.snow_depths [self.x] , "output/" + generateNameT("depth", self.x))
		print "Complete."
		
		os.system('cls' if os.name == 'nt' else 'clear')
		print "\n\n    (3 / 8) Preparing precipitation event rasters\n"
		# translate snow depth changes into m
		for self.x in range (0, timesteps):
			if self.x < 1:
				self.snow_m.append(self.snow_depths[self.x])
			else:
				self.snow_m.append(max(scalar(0),self.snow_depths[self.x] - self.snow_depths[self.x - 1]))
			
			report (self.snow_m [self.x] , "output/" + generateNameT("snowm", self.x))
			print "-",
		print "Complete."	
		
		# -- Load All Snow Temperature Rasters --
		self.dtf_ff = "v1"
		self.dtf_ppppS = "1038wS"
		self.dtf_vvvv = "__"
		self.dtf_Ttttt = "A0024"
		self.dtf_TS = "TS"
		self.dtf_I = "D"
		self.dtf_POOO = "P001"

		os.system('cls' if os.name == 'nt' else 'clear')		
		print "\n\n    (4 / 8) Loading all snow temperature rasters\n"
		for self.x in range (0, timesteps):
			self.current_date = date (self.STARTING_DATE.tm_year, self.STARTING_DATE.tm_mon, self.STARTING_DATE.tm_mday) + timedelta(self.x)
			self.file_name = self.dtf_rrmmm + self.dtf_ff + self.dtf_ppppS + self.dtf_vvvv + self.dtf_Ttttt + self.dtf_oooo + self.dtf_TS + self.current_date.strftime ('%Y%m%d') + "05" + self.dtf_I + self.dtf_POOO
			self.snow_temps.append(self.readmap ("snowdata/" + self.file_name) - scalar (273))
			print "-",
			report (self.snow_temps [self.x], "output/" + generateNameT("temp", self.x))
		print "Complete."	
		
		# -- Load All Sublimation Rasters --
		self.dtf_ff = "v1"
		self.dtf_ppppS = "1050"
		self.dtf_vvvv = "lL00"
		self.dtf_Ttttt = "T0024"
		self.dtf_TS = "TS"
		self.dtf_I = "D"
		self.dtf_POOO = "P000"

		os.system('cls' if os.name == 'nt' else 'clear')		
		print "\n\n    (5 / 8) Loading all snow sublimation rasters\n"
		for self.x in range (0, timesteps):
			self.current_date = date (self.STARTING_DATE.tm_year, self.STARTING_DATE.tm_mon, self.STARTING_DATE.tm_mday) + timedelta(self.x)
			self.file_name = self.dtf_rrmmm + self.dtf_ff + self.dtf_ppppS + self.dtf_vvvv + self.dtf_Ttttt + self.dtf_oooo + self.dtf_TS + self.current_date.strftime ('%Y%m%d') + "05" + self.dtf_I + self.dtf_POOO
			self.snow_sublimations.append(self.readmap ("snowdata/" + self.file_name) - scalar (273))
			print "-",
			report (self.snow_sublimations [self.x], "output/" + generateNameT("subl", self.x))
		print "Complete."	
		
		# -- Load All Snow Melt Rasters --
		self.dtf_ff = "v1"
		self.dtf_ppppS = "1044"
		self.dtf_vvvv = "bS__"
		self.dtf_Ttttt = "T0024"
		self.dtf_TS = "TS" #yyyymmdd "05"
		self.dtf_I = "D"
		self.dtf_POOO = "P000"
	
		os.system('cls' if os.name == 'nt' else 'clear')	
		print "\n\n    (6 / 8) Loading all snowmelt rasters\n"
		for self.x in range (0, timesteps):
			self.current_date = date (self.STARTING_DATE.tm_year, self.STARTING_DATE.tm_mon, self.STARTING_DATE.tm_mday) + timedelta(self.x)
			self.file_name = self.dtf_rrmmm + self.dtf_ff + self.dtf_ppppS + self.dtf_vvvv + self.dtf_Ttttt + self.dtf_oooo + self.dtf_TS + self.current_date.strftime ('%Y%m%d') + "05" + self.dtf_I + self.dtf_POOO
			self.snow_melts.append(self.readmap ("snowdata/" + self.file_name))
			print "-",
			report (self.snow_melts [self.x], "output/" + generateNameT("melt", self.x))
		print "Complete."	
		
		# -- Load All Blowing Snow Sublimation Rasters --
		self.dtf_ff = "v1"
		self.dtf_ppppS = "1039"
		self.dtf_vvvv = "lL00"
		self.dtf_Ttttt = "T0024"
		self.dtf_TS = "TS" #yyyymmdd "05"
		self.dtf_I = "D"
		self.dtf_POOO = "P000"
	
		os.system('cls' if os.name == 'nt' else 'clear')	
		print "\n\n    (7 / 8) Loading all blowing snow sublimation rasters\n"
		for self.x in range (0, timesteps):
			self.current_date = date (self.STARTING_DATE.tm_year, self.STARTING_DATE.tm_mon, self.STARTING_DATE.tm_mday) + timedelta(self.x)
			self.file_name = self.dtf_rrmmm + self.dtf_ff + self.dtf_ppppS + self.dtf_vvvv + self.dtf_Ttttt + self.dtf_oooo + self.dtf_TS + self.current_date.strftime ('%Y%m%d') + "05" + self.dtf_I + self.dtf_POOO
			self.blowing_snows.append(self.readmap ("snowdata/" + self.file_name))
			print ".",
			report (self.blowing_snows [self.x], "output/" + generateNameT("blowsnow", self.x))
		print "Complete."

		os.system('cls' if os.name == 'nt' else 'clear')		
		
		# All loading and pre-processing is complete
		print "\n\n    (8 / 8) Running dynamic model\n"
	
	# The dynamic model that iterates over a number of time steps
	def dynamic (self):

		self.dyn_temp = self.readmap ("output/temp")							# Reads the snow temperature raster for the current time step
		self.dyn_snowfall = self.readmap ("output/snowm")						# Reads the snow accumulation event raster for the current time step
		self.dyn_rainfall = self.readmap ("output/rainfall")					# Reads the 24-hour rainfall for the current time step
		self.dyn_snowmelt = self.readmap ("output/melt")						# Reads the snow melt for the current time step
		self.dyn_sublimation = self.readmap("output/subl")						# Reads the snow sublimation raster for the current time step
		self.dyn_blowingsnow = self.readmap ("output/blowsnow")					# Reads the blowing snow sublimation raster for the current time step
		self.dyn_snowdepth = self.readmap ("output/depth")						# Reads the snow depth raster for the current time step
		self.temp_min = (scalar (0) - self.dyn_temp) * scalar(2)			 	# Minimum snow temperature: assumes average snowpack temperature is the median and constructs a lowest temperature value
		
		self.temperature_gradient = scalar(self.temp_min / self.dyn_snowdepth)  # Vertical temperature gradient in the snow (top to bottom)
		
		self.melt_days = cover( ifthenelse ( self.dyn_snowmelt == scalar (0), scalar(0), self.melt_days + scalar(1) ), scalar(0) ) # Number of days with melting snow
		self.non_precip_days = cover( ifthenelse ( pcrand( self.dyn_snowfall < self.stabilizer_nonprecip_amt, self.dyn_rainfall == scalar(0) ), self.non_precip_days + scalar(1), scalar(0) ), scalar(0) )
		
		self.stable_factor = cover( ifthenelse ( pcrand( pcrand ( self.non_precip_days >= self.stabilizer_nonprecip_days, self.temperature_gradient <= self.temp_gradient_et ), self.dyn_blowingsnow > self.stabilizer_min_blowing_snow ), self.stable_factor + scalar(1), scalar(0) ) , scalar (0) )
		self.mlrfp = ifthenelse( pcror( self.stable_factor >= self.mlrfp_stabilization_days, pcrand( (self.dyn_blowingsnow / scalar(-100000) ) > self.mlrfp_depth, self.mlrfp_depth < self.weak_layer_burial_depth) ), scalar (0), self.mlrfp )
		self.rrfp = ifthenelse( pcror( self.stable_factor >= self.rrfp_stabilization_days, pcrand( (self.dyn_blowingsnow / scalar(-100000) ) > self.rrfp_depth, self.rrfp_depth < self.weak_layer_burial_depth) ), scalar (0), self.rrfp )
		self.wsp = ifthenelse( pcror( self.melt_days >= self.wet_slab_melt_days, self.dyn_rainfall > scalar(0) ), scalar(1), scalar(0) )
		
		# Calculates formation of facets by radiation recrystallization
		self.rrfp = cover( max( self.rrfp,ifthenelse ( pcrand( pcrand( self.dyn_sublimation <= self.rrfp_max_sublimation, self.dyn_snowmelt == scalar(0) ), self.dyn_temp < scalar(-2)), scalar (1), scalar (0))),scalar(0))
		self.rrfp_depth = cover( self.rrfp * ( self.rrfp_depth + self.dyn_snowfall), scalar(0) )
		self.rrfp = cover( ifthenelse ( self.rrfp_depth > scalar(1), scalar(0), self.rrfp ), scalar(0) )
		self.rrfp_depth = cover( self.rrfp_depth * self.rrfp, scalar(0) )
		
		self.mlrfp = cover( max( self.mlrfp, ifthenelse ( pcrand  ( pcror( self.dyn_snowmelt > scalar(0), self.dyn_rainfall > scalar(0) ), pcrand( self.dyn_snowfall > scalar(0), self.dyn_snowfall < scalar (0.1) ) ), scalar (1), scalar (0) ) ), scalar(0) )
		self.mlrfp_depth = cover( self.mlrfp * (self.mlrfp_depth + self.dyn_snowfall), scalar(0) )
		self.mlrfp = cover( ifthenelse( self.mlrfp_depth > scalar(1), scalar(0), self.mlrfp ),scalar(0) )
		self.mlrfp_depth = cover( self.mlrfp_depth * self.mlrfp, scalar(0) )
		
		self.temperature_gradient_exceeded = ifthenelse( self.temperature_gradient > self.temp_gradient_tg, scalar (1), scalar (-1) )
		self.dhp_indicator_r = scalar(self.dhp_indicator_r) + scalar(self.temperature_gradient_exceeded)
		self.dhp_indicator_r = ifthenelse ( scalar(self.dhp_indicator_r) < scalar(-5), scalar(-5), scalar(self.dhp_indicator_r) )
		self.dhp_indicator_r = cover( ifthenelse (self.dhp_indicator_r > scalar(30), scalar(30), scalar(self.dhp_indicator_r) ), scalar(-1) )
		
		# Reset all stability indicators to 0 if no snow cover
		self.mlrfp = ifthenelse (self.dyn_snowdepth > scalar(0), self.mlrfp, scalar(0))
		self.rrfp = ifthenelse (self.dyn_snowdepth > scalar(0), self.rrfp, scalar(0))
		self.wsp = ifthenelse (self.dyn_snowdepth > scalar(0), self.wsp, scalar(0))
		self.dhp_indicator_r = ifthenelse (self.dyn_snowdepth > scalar(0), self.dhp_indicator_r, scalar(0))
		self.stable_factor = ifthenelse (self.dyn_snowdepth > scalar(0), self.stable_factor, scalar(0))	
		
		report (self.dhp_indicator_r, "output/" + generateNameT("dpthhoar", self.currentTimeStep()))
		report (self.wsp, "output/" + generateNameT("wetslab", self.currentTimeStep()))
		report (self.mlrfp, "output/" + generateNameT("mlrfprob", self.currentTimeStep()))
		report (self.rrfp, "output/" + generateNameT("rrfprob", self.currentTimeStep()))
		
		self.unstable_snow = max(ifthenelse (pcrand(self.dhp_indicator_r > self.dhp_trigger_threshold, self.dyn_snowdepth < scalar (1)), scalar(1), scalar (0)) + scalar(self.rrfp_depth > self.weak_layer_burial_depth) + scalar(self.mlrfp > self.weak_layer_burial_depth) - scalar (self.stable_factor > scalar(0)) + scalar(self.wsp), scalar(0))
		self.alptruth_u = ifthenelse (self.unstable_snow > scalar(1), scalar(1), scalar (0))
		report (self.unstable_snow, "output/" + generateNameT("unstable", self.currentTimeStep()))
		report (self.alptruth_u, "output/" + generateNameT("alptruth", self.currentTimeStep()))
	

ssModel = SnowStabilityModel("clone_co.map")
dynSSModel = DynamicFramework (ssModel, timesteps-1)
dynSSModel.run()
