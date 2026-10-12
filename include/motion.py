import os
import math
import numbers

class motion(object):
	
	def __init__(self,inX,inY,inRad):
		self.M_2PI = 6.28318530718
		self.circle_div = 256
		self.cx = inX
		self.cy = inY
		self.rad = inRad
		self.ang = 0
		self.a_step = self.M_2PI / self.circle_div
		
	def get_pos(self):
		xp = self.cx+self.rad*math.cos(self.ang)
		yp = self.cy+self.rad*math.sin(self.ang)
		self.ang += self.a_step
		return "["  + str(xp) + ","+str(yp)+"]"