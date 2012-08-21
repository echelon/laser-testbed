#!/usr/bin/env python

"""

THIS IS AN EXCELLENT TOOL TO UNDERSTAND BLANKING!

PLAY WITH THE VARIABLES BELOW

I'm writing this to learn how to effectively do blanking.

Generates a random point, blanks to the next random point. 
I need to be kind to the galvos...
"""

from daclib import dac
from daclib.common import * 

import random 
import math
import itertools
import sys
import time

MAXPT = 32330 # Canvas boundaries 
POINT_DURATION  = 5000 # How long to draw point
BLANK_SAMPLE_PTS = 5000 # How long to blank 
LASER_POWER_DENOM = 5 # How much to divide power by
SHOW_BLANKING_PATH = True # Show blanking trace

"""
Send the galvo to random points...
"""
class BlinkPointStream(object):

	def __init__(self):
		self.called = False
		self.stream = self.produce()

	def produce(self):
		while True: 
			x = random.randint(-MAXPT, MAXPT)
			y = random.randint(-MAXPT, MAXPT)
			for i in xrange(0, POINT_DURATION):
				yield (x, y, 0, 0, CMAX/LASER_POWER_DENOM)

	def read(self, n):
		d = [self.stream.next() for i in xrange(n)]
		return d

"""
Now with "blanking"... 
"""
class BlinkPointStreamWithBlanking(BlinkPointStream):

	def produce(self):
		lastX = 0
		lastY = 0
		while True: 
			x = random.randint(-MAXPT, MAXPT)
			y = random.randint(-MAXPT, MAXPT)
			
			# Do blanking first.
			xDiff = lastX - x
			yDiff = lastY - y
			mv = BLANK_SAMPLE_PTS
			for i in xrange(0, mv): 
				percent = i/float(mv)
				xb = int(lastX - xDiff*percent)
				yb = int(lastY - yDiff*percent)
				#print "Blank at: %d, %d" % (xb, yb)
				if SHOW_BLANKING_PATH:
					# XXX: "See" the blanking
					yield (xb, yb, CMAX/LASER_POWER_DENOM,
								   CMAX/LASER_POWER_DENOM,
								   CMAX/LASER_POWER_DENOM)
				else:
					yield (xb, yb, 0, 0, 0)

			# Show the random point
			for i in xrange(0, POINT_DURATION):
				yield (x, y,  
						 CMAX/LASER_POWER_DENOM,
						 CMAX/LASER_POWER_DENOM,
						 CMAX/LASER_POWER_DENOM)

			lastX = x
			lastY = y

while True:
	try:
		d = dac.DAC(dac.find_first_dac())
		#ps = BlinkPointStream()
		ps = BlinkPointStreamWithBlanking()
		d.play_stream(ps)

	except KeyboardInterrupt:
		sys.exit()

	except:
		# Hopefully the galvos aren't melting... 
		print "EXCEPTION"
		time.sleep(5.0)
		continue


