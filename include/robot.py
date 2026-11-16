import os
import math
import numbers
import math
from row64tools.bytestream import bytestream as bStream
from include.geodist import geodist
from include.geom import geom
from include.geofence import geofence


class robot(object):
	
	def __init__(self):
		self.loaded = False
		self.load()
		self.gtime = 0 # time entered geo-fence

	def load(self):
		
		# --------- read geo motion file to lookup positions ---------
		fPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "robot_paths.geom")
		self.gm = geom(fPath)
		
		# --------- read geo dist file to accelerate distances ---------
		sPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "shelve_stations.geodist")
		self.gd = geodist(sPath)

		# --------- read geofence for shape collision ---------
		fPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "gfence.geof")
		self.gf = geofence(fPath)

		# --------- use the xy and names from the geodist ---------
		self.P = self.gd.P # xy of points 
		self.pn = self.gd.pn # point names
		self.shelf = {} # shelf status, any shelf in the dict is gathered
		self.loaded = True

	def empty_shelves(self):
		sd = [[],[],[]]
		for i in range(len(self.pn)):
			sd[0].append(self.pn[i])
			sd[1].append(1)
			sd[2].append(16777215) # white
		return sd

	def get_timestr(self, inH):
		hour = int(inH)
		mdec = (inH - hour) * 60
		minutes = int(mdec)
		mseconds = mdec - minutes
		seconds = int(mseconds * 60)
		if hour < 1: hour = 12
		elif hour > 24:hour -= 24
		return str(hour)+":"+str(minutes).zfill(2)+":"+str(seconds).zfill(2)

	def add_to_log(self, inLog, inStr, inHour):
		inLog[0].append(inStr)
		inLog[1].append(self.get_timestr(inHour))
		inLog[0] = inLog[0][-15:]
		inLog[1] = inLog[1][-15:]
		
	def shelf_proximity(self, inD, inReset, inHour, inLog):
		if inReset:
			if len(self.shelf) > 0:self.add_to_log(inLog,"Completed Picking Order",inHour)
			self.shelf.clear()

		if len(inD)==0 or len(inD[2])==0:return self.empty_shelves()
		else: 
			for i in range(len(self.P)): # check robot has arrived at pick target
				dist = self.gd.GetDist( inD[2][0],inD[3][0],self.P[i][0],self.P[i][1])
				if dist != -1 and dist < 10:
					if self.pn[i] not in self.shelf:
						self.add_to_log(inLog, "Picked Item: "+self.pn[i], inHour)
						self.shelf[self.pn[i]] = True
		sd = [[],[],[]]
		for n in self.pn:
			sd[0].append(n)
			sd[1].append(1)
			if n in self.shelf:sd[2].append(255) # gathered shelf blue 0000FF
			else:sd[2].append(16777215) # white FFFFFF

		collide = self.gf.get_id(inD[2][0],inD[3][0]) # check edge hit of geo-fence area
		if self.gtime == 0 and collide > -1:  # enter geo-fence
			self.add_to_log(inLog, "Enter: Home Electronics", inHour)
			self.gtime = inHour
		elif self.gtime > 0 and collide == -1: # exit geo-fence
			nbsec = int((inHour - self.gtime) * 60 * 100)/100
			self.add_to_log(inLog, "Exit: "+str(nbsec)+"s in Home Electronics", inHour)
			self.gtime = 0
		return sd
	
	def get_data(self, inDHour):
		rtn = self.gm.get_motion(inDHour) # get motion path name and current coordinates
		perc = 1 - (5.67 - inDHour)/ .17 # motion loop from decimal hour 5.5 to 5.67
		return [rtn[2], [perc]*len(rtn[0]) ,rtn[0], rtn[1]] # fill to match our dataframe