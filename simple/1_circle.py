#!/usr/bin/env python

from daclib import dac
from daclib.common import * 

import math
import itertools
import sys

class CirclePointStream(object):

	def produce(self):

		MAXRAD =  32600

		USERAD = int( MAXRAD / 8)
	
		RESIZE_SPEED_INV  = 200

		PTS = 100
		while True: 
			rad = int(USERAD)
			for i in xrange(0, PTS, 1):
				i = float(i) / PTS * 2 * math.pi
				x = int(math.cos(i) * rad)
				y = int(math.sin(i) * rad) 
				yield (x, y, CMAX/4, CMAX/4, CMAX/4) 

	def __init__(self):
		self.called = False
		self.stream = self.produce()

	def read(self, n):
		d = [self.stream.next() for i in xrange(n)]
		return d

d = dac.DAC("169.254.206.40")

ps = CirclePointStream()
d.play_stream(ps)
