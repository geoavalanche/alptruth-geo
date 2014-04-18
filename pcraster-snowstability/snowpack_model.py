from pcraster.framework import *
from array import array
import time
from datetime import date, timedelta

timesteps = 120;

class SnowStabilityModel(DynamicModel):
	def __init__(self, cloneMap):
		DynamicModel.__init__(self)
		setclone(cloneMap)
	def initial (self):
		# Build the filename string -- Masked daily FTP tars NSIDC SNODAS
		# rr_mmmffppppSvvvvTttttooooTSyyyymmddhhIPOOO.xxx.gz
		self.iter = 0;
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

		#loadit
		self.file_name = self.dtf_rrmmm + self.dtf_ff + self.dtf_ppppS + self.dtf_vvvv + self.dtf_Ttttt + self.dtf_oooo + self.dtf_TS + self.dtf_tstamp + self.dtf_I + self.dtf_POOO
		# snowdata/us_ssmv01025SlL01T0024TTNATS2013111105DP001.map
		self.snowfall_1 = self.readmap ("snowdata/" + self.file_name)

		self.dtf_tstamp = "2013112305"
		self.file_name = self.dtf_rrmmm + self.dtf_ff + self.dtf_ppppS + self.dtf_vvvv + self.dtf_Ttttt + self.dtf_oooo + self.dtf_TS + self.dtf_tstamp + self.dtf_I + self.dtf_POOO
		#print self.file_name
		self.snowfall_2 = self.readmap ("snowdata/" + self.file_name)

		report (self.snowfall_1 + self.snowfall_2, "test_results.map")
		
		
	
	def dynamic (self):
		#print self.currentTimeStep()
		self.current_date = date (self.STARTING_DATE.tm_year, self.STARTING_DATE.tm_mon, self.STARTING_DATE.tm_mday) + timedelta(self.currentTimeStep()-1)
		self.dtf_tstamp = "2013112305"
		self.file_name = self.dtf_rrmmm + self.dtf_ff + self.dtf_ppppS + self.dtf_vvvv + self.current_date.strftime ('%Y%m%d') + "05" + self.dtf_oooo + self.dtf_TS + self.dtf_tstamp + self.dtf_I + self.dtf_POOO
		self.current_snow = self.readmap ("snowdata/" + self.file_name)
		#report(self.current_snow, "results/test.map")
		#self.iter += 1

ssModel = SnowStabilityModel("clone.map")
dynSSModel = DynamicFramework (ssModel, timesteps)
dynSSModel.run()
