import os
import math
import numbers
import math
# from row64tools.bytestream import bytestream as bStream
from include.randlib import randlib

class jetson(object):
    
    def __init__(self):
        self.rlib = randlib()
    
    def get_data(self, inStat, inDTime, inPerc, inFlip):
        inStat[0].insert(0,inDTime)
        perc = inPerc
        if inFlip: perc = 1 - inPerc
        layer = (perc * 10) % 1
        layer2 = ((1- perc) * 36) % 1
        perc2 = 1-perc
        # use stream random library to generate system stats over time
        inStat[1].insert(0,self.rlib.get_lperc(inPerc * .1, inPerc) * 100 + 10) # GPU
        inStat[2].insert(0,self.rlib.get_layer_perc(perc,layer,.7) * 5993 + 217) # Power Consumption (milliwatts)
        miniLayer = self.rlib.get_layer_perc(perc,layer2,.7)
        inStat[3].insert(0,miniLayer * 4 + 54) # Temp_GPU - Degress Celsius
        miniLayer3 = self.rlib.get_layer_perc(1-perc,layer,.8)
        inStat[4].insert(0,self.rlib.get_perc() + miniLayer*.2 * 6 + 50)  # Temp_CPU
        inStat[5].insert(0,miniLayer3 + miniLayer*.12 * 6 + 49) # Temp_Soc0
        inStat[6].insert(0,self.rlib.get_perc() * 7 + 47) # Temp_Soc1
        inStat = [subStat[:100] for subStat in inStat]
        return inStat