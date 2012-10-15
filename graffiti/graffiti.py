#!/usr/bin/env python

"""
Draw Graffiti Markup Language (GML) files with the laser.
The files included with this project are from the website
http://000000book.com/, which houses thousands of GML
examples.

This is very primitive at the moment, but I hope to
expand this to enable realtime drawing on a tablet or
other device.
"""

import os
import math
import itertools
import sys
import time
import thread

# Graffiti Markup Language
import PyGML

from lib import dac
from lib.common import *
from lib.stream import PointStream
from lib.shape import Shape


"""
CONFIGURATION
"""

LASER_POWER_DENOM = 1.0

"""
Globals
"""

obj = None
ps = None


"""
Animation code / logic
"""

def getGml(fn):
	f = open(fn, 'r')
	g = PyGML.GML(f)
	f.close()
	return g

class Graffiti(Shape):

	def __init__(self, x = 0, y = 0,
			r = 0, g = 0, b = 0, filename=None):
		super(Graffiti, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.theta = 0
		self.thetaRate = 0

		self.gml = getGml(filename)

	def produce(self):
		"""
		Generate the points of the circle.
		"""
		r, g, b = (0, 0, 0)

		for stroke in self.gml.iterStrokes():
			for pt in stroke.iterPoints():
				x = pt.x * 20000
				y = pt.y * 20000
				yield (x, y, CMAX, CMAX, CMAX)

		self.drawn = True

def dac_thread():
	global obj
	global ps

	ps.objects.append(obj)

	while True:
		try:
			d = dac.DAC(dac.find_first_dac())
			d.play_stream(ps)

		except KeyboardInterrupt:
			sys.exit()

		except Exception as e:
			import sys, traceback
			print '\n---------------------'
			print 'Exception: %s' % e
			print '- - - - - - - - - - -'
			traceback.print_tb(sys.exc_info()[2])
			print "\n"

"""
def spin_thread():
	global SQUARE
	global SQUARE_X, SQUARE_Y
	global SQUARE_RADIUS_MIN, SQUARE_RADIUS_MAX
	global SQUARE_RADIUS_INC
	global SPIN_THETA_INC
	global PAN_X_INC_MAG, PAN_X_MAX, PAN_X_MIN

	inc = True
	panInc = True

	xPan = 0
	spin = 0

	while True:

		# RADIUS
		r = SQUARE.radius
		if r > SQUARE_RADIUS_MAX:
			inc = False
		elif r < SQUARE_RADIUS_MIN:
			inc = True

		if inc:
			r += SQUARE_RADIUS_INC
		else:
			r -= SQUARE_RADIUS_INC

		SQUARE.radius = r

		# PAN
		if xPan > PAN_X_MAX:
			panInc = False
		elif xPan < PAN_X_MIN:
			panInc = True

		if panInc:
			xPan += PAN_X_INC_MAG
			spin = -SPIN_THETA_INC
		else:
			xPan -= PAN_X_INC_MAG
			spin = SPIN_THETA_INC

		SQUARE.x = SQUARE_X + xPan
		SQUARE.theta += spin

		time.sleep(0.05)
"""

#
# Start Threads
#

def main():
	global obj
	global ps

	cwd = os.path.dirname(__file__)
	fname = "gml/hello.gml"
	if len(sys.argv) > 1:
		fname = sys.argv[1]

	fname = os.path.join(cwd, fname)

	obj = Graffiti(filename=fname)
	ps = PointStream()

	thread.start_new_thread(dac_thread, ())
	time.sleep(1.0)
	#thread.start_new_thread(spin_thread, ())

	while True:
		time.sleep(100000)

if __name__ == '__main__':
	main()
