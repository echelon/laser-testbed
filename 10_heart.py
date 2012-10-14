#!/usr/bin/env python

from daclib import dac
from daclib.common import *

import math
import itertools
import sys

LASER_POWER_DENOM = 1.0
SAMPLE_PTS = 100 # 30 and below very damaging to galvos
SIZE = 500

class HeartPointStream(object):

	def produce(self):
		RESIZE_SPEED_INV = 200
		while True:
			for i in xrange(0, SAMPLE_PTS, 1):
				i = float(i) / SAMPLE_PTS * 2 * math.pi
				x = int(16*math.sin(i)**3)*SIZE
				y = int(13*math.cos(i) - 5*math.cos(2*i) - \
						2*math.cos(3*i) - math.cos(4*i))*SIZE
				#pt = (x, y, CMAX, 0, CMAX/3) # Original color before red died.
				pt = (x, y, CMAX, CMAX, CMAX)
				yield pt

	def __init__(self):
		self.called = False
		self.stream = self.produce()

	def read(self, n):
		d = [self.stream.next() for i in xrange(n)]
		return d

while True:
	try:
		d = dac.DAC(dac.find_first_dac())
		ps = HeartPointStream()
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
