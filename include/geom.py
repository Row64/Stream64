import os
import math
from row64tools.bytestream import bytestream as bStream

# Geo Motion on poly-lines with a time range (24 hour decimal time start/stop)
class geom: 
    
    def __init__(self, inPath):
        self.bs = bStream()
        self.bs.read(inPath)
        self.TGRID = self.bs.get_uint32_vector2d("T_grid")
        self.GSize = self.bs.get_uint32("T_gridsize")
        self.S_nbl = self.bs.get_uint32("S_nbl")
        self.BB = self.bs.get_double_vector("S_bb")
        self.SName = self.bs.get_string_vector("S_name")
        self.xi = self.bs.key_ind("S_x")
        self.yi = self.bs.key_ind("S_y")
        self.di = self.bs.key_ind("S_d")
        self.li = self.bs.key_ind("S_look")
        self.xyii = self.bs.key_ind("S_xyi")
        self.sidi = self.bs.key_ind("T_sid")
        self.ski = self.bs.key_ind("T_start")
        self.dki = self.bs.key_ind("T_dur")
        self.ni = self.bs.key_ind("S_name")

    # ------------------------------ get_motion ------------------------------
    # returns a list of positions and names of all motion path points 
    # at a given time.  Time is in decial hours (ex: 3.5 = 3:30)
    # returns list of [ [x1,x2..], [y1,y2..], [name1,name2..] ]
    # returns [[],[],[]] if all motion paths are outside any time range
    # ------------------------------------------------------------------------
    def get_motion(self, inDHour): 
        rtn = [[],[],[]]
        gi = math.floor( (inDHour / 24.0) * self.GSize )
        pList = []
        for ti in self.TGRID[gi]:
            i = self.bs.get_uint32_vector_item(self.sidi, ti)
            dur = self.bs.get_float_vector_item(self.dki,ti)
            if dur < .00001:continue
            perc = (inDHour-self.bs.get_float_vector_item(self.ski,ti))/dur
            if perc >= 0 and perc <= 1:
                xb = 0;yb = 0;bi = i * 4
                maxI = self.bs.get_uint32_vector_item(self.xyii,i+1)-1
                total = self.bs.get_float_vector_item(self.di,maxI)
                tdist = total * perc
                if tdist < 0.00001:
                    minI = self.bs.get_uint32_vector_item(self.xyii,i)
                    xb = self.bs.get_uint16_vector_item(self.xi,minI)
                    yb = self.bs.get_uint16_vector_item(self.yi,minI)
                elif tdist > total:
                    xb = self.bs.get_uint16_vector_item(self.xi,maxI)
                    yb = self.bs.get_uint16_vector_item(self.yi,maxI)
                else:
                    lowerI = math.floor(perc * (self.S_nbl-1)) + i * (self.S_nbl-1);
                    upperI = self.bs.get_uint16_vector_item(self.li,lowerI)+1
                    upperVal = 0
                    while True:
                        upperVal = self.bs.get_float_vector_item(self.di,upperI)
                        if upperVal > tdist: break
                        if upperVal == maxI: break
                        upperI = upperI+1
                    lowerI = upperI - 1
                    lowerV = self.bs.get_float_vector_item(self.di,lowerI)
                    subPerc = (tdist - lowerV)/(self.bs.get_float_vector_item(self.di,upperI) - lowerV)
                    xb = (subPerc)*(float(self.bs.get_uint16_vector_item(self.xi,upperI)))+(1-subPerc)*(float(self.bs.get_uint16_vector_item(self.xi,lowerI)))
                    yb = (subPerc)*(float(self.bs.get_uint16_vector_item(self.yi,upperI)))+(1-subPerc)*(float(self.bs.get_uint16_vector_item(self.yi,lowerI)))
                rtn[0].append(self.BB[bi] + (xb * 0.000015259) * self.BB[bi+2])
                rtn[1].append(self.BB[bi+1] + (yb * 0.000015259) * self.BB[bi+3])
                rtn[2].append(self.bs.get_string_vector_item(self.ni,i))
        return rtn
