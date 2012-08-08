
from .Geo import *

class CircleGeo(PointStream):

	def __init__(self, radius=32600):
		"""
		Create a circle.
		"""

		super(CircleGeo, self).__init__()

		if radius > 32600:
			radius = 32600

		self.radius = radius

		"""
		A list of the point/colors to draw. 
		Includes internal blanking, etc.
		"""
		self.points = []
		self.create_points()

	def create_points(self):
		"""
		Generate the geometry.
		Keep the points in memory. 
		"""
		CMAX = 65535 # MAX COLOR VALUE (TODO: Duplicated)
		rad = int(self.radius)
		for i in xrange(0, 1000, 1):
			i = float(i) / 1000 * 2 * math.pi
			x = int(math.cos(i) * rad)
			y = int(math.sin(i) * rad) 
			self.points.append((x, y, CMAX, CMAX, CMAX))

