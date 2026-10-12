import os
import math
from row64tools.bytestream import bytestream as bStream

class geodist:
    
    def __init__(self, inPath):
        bs = bStream()
        bs.read(inPath)
        self.P = bs.get_double_vector2d("P") # xy of points 
        self.pn = bs.get_string_vector("Names") # point names
        self.BB = bs.get_double_vector("BB")
        self.Rx1 = bs.get_double_vector("Rx1")
        self.Ry1 = bs.get_double_vector("Ry1")
        self.Rx2 = bs.get_double_vector("Rx2")
        self.Ry2 = bs.get_double_vector("Ry2")
        self.GDivX = bs.get_uint32("GDivX")
        self.GDivY = bs.get_uint32("GDivY")
        self.GRID = bs.get_uint32_vector2d("GRID")
        self.GDivXBBW = bs.get_double("GDivXBBW")
        self.GDivYBBH = bs.get_double("GDivYBBH")

    def GetDist(self, x1, y1, x2, y2): # returns -1 = outside distance, else distance
        ix = int( (x1-self.BB[0]) * self.GDivXBBW )
        iy = int( (y1-self.BB[1]) * self.GDivYBBH )
        if ix<0 or iy<0 or ix>=self.GDivX or iy>=self.GDivY:return -1
        for i in self.GRID[(iy*self.GDivX)+ix]:
            if  y1<self.Ry2[i] and y1>self.Ry1[i] and x1<self.Rx2[i] and x1>self.Rx1[i]:
                return math.dist([x1, y1],[x2, y2])
        return -1