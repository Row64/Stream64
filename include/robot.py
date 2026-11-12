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
		# self.bs = bStream() # geo motion
		self.load()

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
	
	def shelf_proximity(self, inD, inReset):
		if inReset:self.shelf.clear()
		
		if len(inD)==0 or len(inD[2])==0:return self.empty_shelves()
		else: # if we are near a shelf, register it as gathered
			for i in range(len(self.P)):
				dist = self.gd.GetDist( inD[2][0],inD[3][0],self.P[i][0],self.P[i][1])
				if dist != -1 and dist < 10:self.shelf[self.pn[i]] = True

		collide = self.gf.get_id(inD[2][0],inD[3][0])
		# print(" collide with:", collide)

		sd = [[],[],[]]
		for n in self.pn:
			sd[0].append(n)
			sd[1].append(1)
			if n in self.shelf:sd[2].append(255) # gathered shelf blue 0000FF
			else:sd[2].append(16777215) # white FFFFFF
		return sd
	
	def get_data(self, inDHour):
		rtn = self.gm.get_motion(inDHour) # get a list of positions and names
		return [rtn[2], [.1]*len(rtn[0]) ,rtn[0], rtn[1]] # fill to match our dataframe