#from __future__ import division
#print str(((self.x+1)/timesteps) * 100) + "%"
from pcraster import *
from pcraster.framework import *
from array import array
import time
import sys
from datetime import date, timedelta

# timesteps is defined in command-line. future: have a default
timesteps = int(sys.argv[1]);

#setglobaloption("l")

class SnowStabilityModel(DynamicModel):
	def __init__(self, cloneMap):
		DynamicModel.__init__(self)
		setclone(cloneMap)
		
	def initial (self):
		# Build the filename string -- Masked daily FTP tars NSIDC SNODAS
		# rr_mmmffppppSvvvvTttttooooTSyyyymmddhhIPOOO.xxx.gz
		self.iter = 0;
		self.snowfall_layers = list()
		self.snow_depths = list()
		self.snow_temps = list()
		self.snow_sublimations = list()
		self.snow_melts = list()
		self.snow_mm = list()
		self.snow_layers = list()
		self.blank_layers_map = scalar (0)
		self.dhp = scalar (0) # Depth hoar problem indicator
		
		self.load_status = 0;
		self.STARTING_DATE = time.strptime ('20131101' , '%Y%m%d')
		#self.month_lengths = array ("i", [31,28,31,30,31,30,31,31,30,31,30,31])
		# constants in the filename shared by all input data
		self.dtf_rrmmm = "us_ssm"
		self.dtf_oooo = "TTNA"

		# Establish date and year
		self.dtf_tstamp = "20131122" + "05"

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
			
			report (self.snow_mm [self.x] > scalar(10), "output/" + generateNameT("layers", self.x))
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
			self.snow_melts.append(self.readmap ("snowdata/" + self.file_name) - scalar (273))
			print ".",
			report (self.snow_melts [self.x], "output/" + generateNameT("melt", self.x))
		print "Complete."	
		
		print "Running dynamic model..."
		
	def dynamic (self):
		#adds a layer if a snow event exceeds 10mm
		#self.blank_layers_map = ifthenelse (self.readmap ("output/snowmm") > scalar (10), self.blank_layers_map + scalar(1), self.blank_layers_map)
		report (self.readmap ("output/melt") > self.readmap("output/subl"), "output/" + generateNameT("loss", self.currentTimeStep()))
		#removes layer if no snow
		#self.blank_layers_map = ifthenelse (self.readmap ("output/depth") < scalar (5), max(self.blank_layers_map - scalar(1),0), self.blank_layers_map)
		#report (self.blank_layers_map, "output/" + generateNameT("res", self.currentTimeStep()))

		self.tempness = (scalar (0) - self.readmap ("output/temp")) * scalar(2)
		self.tempdepth = self.readmap ("output/depth")
		self.temperature_gradient = scalar(self.tempness / self.tempdepth);
		report ( scalar(self.temperature_gradient) , "output/" + generateNameT("tempgrad", self.currentTimeStep()))
		self.temperature_gradient_exceeded = scalar(ifthenelse(self.temperature_gradient > scalar(10), scalar (1), scalar (-1))) #Temperature gradient is > 1C / cm
		self.dhp = scalar (scalar(self.dhp) + scalar(self.temperature_gradient_exceeded))
		report (scalar(self.temperature_gradient_exceeded), "output/" + generateNameT("test", self.currentTimeStep()))
		self.dhp = scalar(ifthenelse (scalar(self.dhp) < scalar(-10), scalar(10), scalar(self.dhp)))
		self.dhp = cover(scalar(ifthenelse (self.dhp > scalar(14), scalar(14), scalar(self.dhp))),scalar(0))
		#ifthenelse (self.temperature_gradient_exceeded, self.dhp = self.dhp + scalar (1), self.dhp = self.dhp - scalar (1))
		report (scalar(self.dhp), "output/" + generateNameT("dpthhoar", self.currentTimeStep()))
		
		#use depth and temp to determine rudimentary temperature gradients
		#iterate through the whole time period
		#add a snowlayer each iteration checking cells > threshold for layers
		#report (self.snowfall_layers [self.currentTimeStep()] , "output/" + generateNameT("res", self.currentTimeStep()))
		
	

ssModel = SnowStabilityModel("clone_co.map")
dynSSModel = DynamicFramework (ssModel, timesteps-1)
dynSSModel.run()
