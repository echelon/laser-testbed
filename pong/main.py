#!/usr/bin/env python

# Libs
import math
import itertools
import sys

# Project
import dac
from laser_geo.circle import CircleGeo
from compositor import CompositorStream

"""
Constants
"""
CMAX = 65535 # MAX COLOR VALUE

def main():
	"""Main Program"""

	# TODO: Find DAC address
	d = dac.DAC("169.254.206.40")

	cs = CompositorStream()

	c1 = CircleGeo(1000)
	c2 = CircleGeo(2000)
	c3 = CircleGeo(3000)
	c4 = CircleGeo(8000)

	cs.geometries.append(c1)
	cs.geometries.append(c2)
	cs.geometries.append(c3)
	#cs.geometries.append(c4)

	d.play_stream(cs)

if __name__ == '__main__': 
	main()
