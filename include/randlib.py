import os
import math
import numbers
import math
import random

from row64tools.bytestream import bytestream as bStream

class randlib(object):
	
	def __init__(self):
		qPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "quantile.ldb")
		bs = bStream()
		bs.read(qPath)
		self.len = bs.get_int32("Len")
		self.nb = bs.get_int32("Nb")
		self.Quantile = bs.get_float_vector2d("Quantile")
	
	def get_lperc(self, inPerc, inBankPerc): 
		# randomness that is coherent over time
		# not blending between samples, get closest sample
		bankI = int(inBankPerc * self.nb)
		curveI = int(inPerc * self.len)
		return self.Quantile[bankI][curveI]

	def get_layer_perc(self, inPerc, inBankPerc, inLayerPerc): 
		# randomness is divided into 2 layers
		# bottom layer is normal (linear) randomness
		# top layer is probabily curve bank that is more coherent over time
		bottomPerc = (1-inLayerPerc) * self.get_perc()
		topPerc = inLayerPerc * self.get_lperc(inPerc, inBankPerc)
		return bottomPerc + topPerc # between 0 and 1

	def get_xperc(self, inSeed):
		# Xor Random Perc - 0 to 1 random number
		inSeed = inSeed ^ (inSeed << 21)
		inSeed = inSeed ^ (inSeed >> 31)
		inSeed = inSeed ^ (inSeed << 4)
		xperc = inSeed / float(0xffffffff)
		return xperc

	def get_perc(self):
		# general random perc, mix of Python random & xor random
		seed = random.randrange(100)
		if self.get_xperc(seed + 37) > 0.5:return self.get_xperc(seed)
		return self.get_sperc()

	def get_sperc(self):
		# Mersenne Twister is used in python's random library
		return random.uniform(0, 1)

	def get_xrand(self, inSeed):
		# Algorithm "xor" from p. 4 of Marsaglia, "Xorshift RNGs"
		inSeed = inSeed ^ (inSeed << 13)
		inSeed = inSeed ^ (inSeed >> 17)
		inSeed = inSeed ^ (inSeed << 5)
		return inSeed


		