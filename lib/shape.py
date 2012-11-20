"""
Based on laser-asteroids/entity.py
"""

class Shape(object):

	# Static object counter. 
	ID_COUNTER = 0

	def __init__(self, x = 0, y = 0,
			r = 0, g = 0, b = 0):

		# Positioning stuff
		self.x = x
		self.y = y
		self.xVel = 0.0
		self.yVel = 0.0
		self.scale = 1.0
		self.rotation = 0.0

		# Drawing specifics 
		self.r = r
		self.g = g
		self.b = b
		self.doBlanking = True # should get blanking? 
		self.skipDraw = False
		self.destroy = False # TODO: Remove feature

		# Cached first and last points. 
		# (Part of the PointStream algo.)
		self.firstPt = (0, 0, 0, 0, 0)
		self.lastPt = (0, 0, 0, 0, 0)

		# Id handling
		self.entityId = Shape.ID_COUNTER
		Shape.ID_COUNTER+=1

	def produce(self):
		self.lastPt = (0, 0, 0, 0, 0)
		return self.lastPt

	def cacheFirstPt(self):
		"""
		I need to cache the first point generated so
		that I can slowly advance the galvos to the
		next object without starting drawing.
		"""
		for x in self.produce():
			self.firstPt = x
			break

