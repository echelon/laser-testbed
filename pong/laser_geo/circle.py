from .Geo import *

import math

class CircleGeo(Geometry):

	def __init__(self, radius=32600):
		"""
		Create a circle.
		"""

		super(CircleGeo, self).__init__()

		if radius > 32600:
			radius = 32600

		self.radius = radius
		self.points = [] # list of tuples of the form (x, y, r, g, b)
		self.create_points()

	def create_points(self):
		"""
		Generate the geometry.
		Keep the points in memory. 
		"""
		CMAX = 65535 # MAX COLOR VALUE (TODO: Duplicated)
		POINTS = 80
		points_ea = POINTS / 4

		x1 = 0
		y1 = 0
		x2 = 0
		y2 = 0
		for i in xrange(0, ea):
			i = float(i) / POINTS * 2 * math.pi
			x = int(math.cos(i) * rad)
			y = int(math.sin(i) * rad) 
			self.points.append((x, y, 0, 0, CMAX))

