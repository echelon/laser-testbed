#!/usr/bin/env python

from daclib import dac
from daclib.common import * 

import math
import itertools
import sys

class SpiralPointStream(object):

	def produce(self):

		MAXRAD =  32600

		USERAD = MAXRAD / 100

		SPIRAL_GROWTH = 14

		BLANK_SAMPLE_PTS = 50

		while True: 
			rad = int(USERAD)
			j = 0

			# Sample 1000 points along the spiral
			for i in xrange(0, 1000, 1):
				i = float(i) / 1000 * 2 * math.pi * SPIRAL_GROWTH
				j = i

				# Spirals are of the form:
				# a*x * trig(x), a is const
				x = int(j * math.cos(i) * rad)
				y = int(j * math.sin(i) * rad)
				yield(x, y, CMAX / 2, CMAX / 2, 0) 

			# Blanking and return to 0,0 smoothly 
			i = float(1000) / 1000 * 2 * math.pi * SPIRAL_GROWTH
			j = i
			x = int(j * math.cos(i) * rad)
			y = int(j * math.sin(i) * rad)
			mv = BLANK_SAMPLE_PTS
			for i in range(1, mv):
				yield(x - x*i/mv, y - y*i/mv, 0, 0, 0) # Slowly move back.

	def __init__(self):
		self.called = False
		self.stream = self.produce()

	def read(self, n):
		d = [self.stream.next() for i in xrange(n)]
		return d

d = dac.DAC("169.254.206.40")

ps = SpiralPointStream()
d.play_stream(ps)


