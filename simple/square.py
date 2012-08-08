#!/usr/bin/env python

from daclib import dac
from daclib.common import * 

import math
import itertools
import sys

def line_generator(pt1, pt2, backward=False, steps = 100):
	xdiff = pt1.x - pt2.x
	ydiff = pt1.y - pt2.y
	if not backward:
		for i in xrange(0, steps, 1):
			j = float(i)/steps
			x = pt1.x + (xdiff * j)
			y = pt1.y + (ydiff * j)
			yield (x, y, CMAX, CMAX, CMAX) # XXX FIX COLORS
	else:
		for i in xrange(steps, 0, -1):
			j = float(i)/steps
			x = pt1.x + (xdiff * j)
			y = pt1.y + (ydiff * j)
			yield (x, y, CMAX, CMAX, CMAX) # XXX FIX COLORS

class LinePointStream(object):

	PTMAX = 32600

	def __init__(self, x1, y1, x2, y2, r=0, g=0, b=0):
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2
		self.pt1 = Point(x1, y1)
		self.pt2 = Point(x2, y2)

		self.r = r
		self.g = g
		self.b = b

		self.stream = self.produce()

		self.lineInGen = line_generator(self.pt1, self.pt2)
		self.lineOutGen = line_generator(self.pt1, self.pt2, backward=True)


		size = 8000
		self.linePts = [
			(Point(0, 0), Point(0, size)),
			(Point(0, -size), Point(-size, -size)),
			(Point(size, -size), Point(size, -2*size)),
			(Point(size, 0), Point(2*size, 0))
		]
		self.curLineIdx = len(self.linePts)-1
		self.advanceLine()

	def advanceLine(self):
		self.curLineIdx = (self.curLineIdx + 1) % len(self.linePts)
		self.curLine = line_generator(self.linePts[self.curLineIdx][0], 
									  self.linePts[self.curLineIdx][1])

	def produce(self):
		while True:
			try:
				yield self.curLine.next()
			except:
				self.advanceLine()

			"""
			# Line out
			for i in xrange(0, steps, 1):
				j = float(i)/steps
				x = self.x1 + (xdiff * j)
				y = self.y1 + (ydiff * j)
				yield (x, y, self.r, self.g, self.b)

			# Line back in
			for i in xrange(0, steps, 1):
				j = float(i)/steps
				x = self.x2 - xdiff * j
				y = self.y2 - ydiff * j
				yield (x, y, self.r, self.g, self.b)
			"""

	def read(self, n):
		d = [self.stream.next() for i in xrange(n)]
		return d

d = dac.DAC("169.254.206.40")

#ps = LinePointStream(-5000, -5000, 5000, 5000, b=CMAX)
ps = LinePointStream(-5000, 0, 500, 500, b=CMAX)
d.play_stream(ps)


