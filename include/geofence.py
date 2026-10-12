import os
from row64tools.bytestream import bytestream as bStream

class geofence:

    def __init__(self, inPath):
        self.BL = [] # UInt8Vector2D
        bs = bStream()
        bs.read( inPath )
        self.BB = bs.get_double_vector("BB")
        self.Rx = bs.get_double_vector("Rx")
        self.Ry = bs.get_double_vector("Ry")
        self.GDivX = bs.get_uint32("GDivX")
        self.GDivY = bs.get_uint32("GDivY")
        self.GRID = bs.get_uint32_vector2d("GRID")
        self.XDiv = bs.get_uint32("XDiv")
        self.YDiv = bs.get_uint32("YDiv")
        self.BL = bs.get_uint8_vector2d("BL")
        self.GDivXBBW = bs.get_double("GDivXBBW")
        self.GDivYBBH = bs.get_double("GDivYBBH")
        self.RwXDiv = bs.get_double_vector("RwXDiv")
        self.RhYDiv = bs.get_double_vector("RhYDiv")

    # first ID hit return.  -1 if no collision, first geofence id if in fence
    def get_id(self, inX, inY):
        ix = int((inX-self.BB[0])*self.GDivXBBW)
        iy = int((inY-self.BB[1])*self.GDivYBBH)
        if ix<0 or iy<0 or ix>=self.GDivX or iy>=self.GDivY:return -1
        llist = self.GRID[(iy*self.GDivX)+ix]
        if len(llist) > 0:
            for i in llist:
                bxi = (int)((inX-self.Rx[i])*self.RwXDiv[i])
                byi = (int)((inY-self.Ry[i])*self.RhYDiv[i])
                if bxi<0 or byi<0 or bxi>=self.XDiv or byi>=self.YDiv: continue
                pi = int(self.XDiv*byi+bxi)
                if (self.BL[i][int(pi/8)]>>pi%8)&1==1:return i
        return -1

    # ID hit list return.  [] if no collision, else list of geofence id's
    def get_ids(self, inX, inY):
        ilist = []
        ix = int((inX-self.BB[0])*self.GDivXBBW)
        iy = int((inY-self.BB[1])*self.GDivYBBH)
        if ix<0 or iy<0 or ix>=self.GDivX or iy>=self.GDivY:return []
        llist = self.GRID[(iy*self.GDivX)+ix]
        if len(llist) > 0:
            for i in llist:
                bxi = (int)((inX-self.Rx[i])*self.RwXDiv[i])
                byi = (int)((inY-self.Ry[i])*self.RhYDiv[i])
                if bxi<0 or byi<0 or bxi>=self.XDiv or byi>=self.YDiv: continue
                pi = int(self.XDiv*byi+bxi)
                if (self.BL[i][int(pi/8)]>>pi%8)&1==1:iList.append(i)
        return ilist