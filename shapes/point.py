#!/usr/bin/env python

from lib import dac
from lib.common import *

import math
import itertools
import sys

LASER_POWER_DENOM = 1.0
SAMPLE_PTS = 100 # 30 and below very damaging to galvos
X = 0
Y = -9000


class PointPointStream(object):
	def produce(self):
		while True:
			yield (X, Y, CMAX/LASER_POWER_DENOM,
					CMAX/LASER_POWER_DENOM,
					CMAX/LASER_POWER_DENOM)

	def __init__(self):
		self.called = False
		self.stream = self.produce()

	def read(self, n):
		d = [self.stream.next() for i in xrange(n)]
		return d

while True:
	try:
		d = dac.DAC(dac.find_first_dac())
		ps = PointPointStream()
		d.play_stream(ps)
	except KeyboardInterrupt:
		sys.exit()
	except Exception as e:
		print e
		continue
