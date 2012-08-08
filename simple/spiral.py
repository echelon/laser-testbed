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

		SPIRAL_DECAY = 10

		while True: 
			rad = int(USERAD)
			j = 0
			for i in xrange(0, 1000, 1):
				i = float(i) / 1000 * 2 * math.pi * 14
				j = i

				# Spirals are of the form:
				# a*x * trig(x), a is const
				x = int(j * math.cos(i) * rad)
				y = int(j * math.sin(i) * rad)
				yield(x, y, CMAX / 2, CMAX / 2, 0) 

			# Blanking
			i = float(1000) / 1000 * 2 * math.pi * 14
			j = i
			x = int(j * math.cos(i) * rad)
			y = int(j * math.sin(i) * rad)
			for i in range(1, 20):
				yield(x - x*i/20 , y - y*i/20, 0, 0, 0)

	def __init__(self):
		self.called = False
		self.stream = self.produce()

	def read(self, n):
		d = [self.stream.next() for i in xrange(n)]
		return d

d = dac.DAC("169.254.206.40")

ps = SpiralPointStream()
d.play_stream(ps)


