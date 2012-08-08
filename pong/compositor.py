"""
This will need to be written when multiple objects are onscreen. It'll 
make a quick assessment about draw order. 

This will likely become incredibly sophisticated as the project matures.
"""

import math
import itertools
import sys

CMAX = 65535 # MAX COLOR VALUE

class CompositorStream(object):

	def __init__(self):
		self.called = False
		self.stream = self.produce()

		self.geometries = []

	def produce(self):
		while True: 

			###
			###  FRAME BEGIN -- draw all geometries. 
			###

			for i in xrange(len(self.geometries)):
				geo = self.geometries[i]
				nextGeo = self.geometries[(i+1)%len(self.geometries)]

				# Draw geo
				for pt in geo.points: 
					yield pt

				# Blank laser to next geo
				lastPt = geo.points[-1]
				nextPt = nextGeo.points[0]

				xDest = nextPt[0]
				yDest = nextPt[1]
				xDiff = xDest - lastPt[0]
				yDiff = yDest - lastPt[1]

				# SAMPLE blanking pts.
				# TODO: In the future, a heuristic for this to make longer
				# paths sample more blanking
				BLANK_POINTS = 100.0
				for i in xrange(1, int(BLANK_POINTS)):
					per = i/BLANK_POINTS
					x = int(xDest - xDiff * per)
					y = int(yDest - yDiff * per)
					yield (x, y, 0, 0, 0, 0, 0, 0)

	
	def read(self, n):
		d = [self.stream.next() for i in xrange(n)]
		return d


