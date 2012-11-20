
CMAX = 65535 # MAX COLOR VALUE
CMIN = 0

class Point(object):
	def __init__(self, x, y):
		self.x = x
		self.y = y
	def __repr__(self):
		return "<Point: %d, %d>" % (self.x, self.y)

class NullPointStream(object):
	def read(self, n):
		return [(0, 0, 0, 0, 0)] * n

