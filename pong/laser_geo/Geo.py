import math
import itertools
import sys

CMAX = 65535 # MAX COLOR VALUE

class PointStream(object):

	def __init__(self):
		self.called = False
		self.points = [(0, 0, CMAX, CMAX, 0)]
		self.stream = self.produce()

	def produce(self):
		while True: 
			for i in xrange(len(self.points)):
				yield self.points[i]
	
	def read(self, n):
		d = [self.stream.next() for i in xrange(n)]
		return d


