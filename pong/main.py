#!/usr/bin/env python

# Libs
import math
import itertools
import sys

# Project
import dac
from laser_geo.circle import CircleGeo
from laser_geo.Geo import PointStream 

"""
Constants
"""
CMAX = 65535 # MAX COLOR VALUE

def main():
	"""Main Program"""

	# TODO: Find DAC address
	d = dac.DAC("169.254.206.40")

	ps = CircleGeo(20000)
	#ps = PointStream()
	d.play_stream(ps)

if __name__ == '__main__': 
	main()
