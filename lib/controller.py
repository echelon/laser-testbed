"""
Represent various videogame controllers
TODO: Various play schemes/configs
XXX: UNTESTED
"""

import re
import pygame

def init_controls():
	"""
	Joystick wrapper.
	"""

	pygame.joystick.init()
	pygame.display.init()

	# Wait until we have joystick
	# TODO: Doesn't handle unplugged
	while not pygame.joystick.get_count():
		print "No joystick detected!"
		time.sleep(5)

	joystick = pygame.joystick.Joystick(0)
	joystick.init()

	if re.search('playstation', joystick.get_name(), re.I):
		return Ps3Controller(joystick)

	elif re.search('playstation', joystick.get_name(), re.I):
		return XboxController(joystick)

	return Controller(joystick)

class Controller(object):

	def __init__(self, joystick):
		"""Pass a PyGame joystick instance."""
		self.js = joystick

	# Call at beginning of main loop
	def getEvent(self):
		return pygame.event.get()

	def getLeftHori(self):
		return 0.0

	def getLeftVert(self):
		return 0.0

	def getRightHori(self):
		return 0.0

	def getRightVert(self):
		return 0.0

	def getLeftTrigger(self):
		return 0.0

	def getRightTrigger(self):
		return 0.0

class XboxController(Controller):

	def __init__(self, joystick):
		super(XboxController, self).__init__(joystick)

	def getLeftHori(self):
		return self.js.get_axis(0)

	def getLeftVert(self):
		return self.js.get_axis(1)

	def getRightHori(self):
		return self.js.get_axis(3)

	def getRightVert(self):
		return self.js.get_axis(4)

	def getLeftTrigger(self):
		# TODO: Verify
		return self.js.get_axis(2)

	def getRightTrigger(self):
		# TODO: Verify
		return self.js.get_axis(5)

class Ps3Controller(Controller):

	def __init__(self, joystick):
		super(Ps3Controller, self).__init__(joystick)

	def getLeftHori(self):
		return self.js.get_axis(0)

	def getLeftVert(self):
		return self.js.get_axis(1)

	def getRightHori(self):
		return self.js.get_axis(2)

	def getRightVert(self):
		return self.js.get_axis(3)

	def getLeftTrigger(self):
		# TODO: Verify
		return self.js.get_axis(12)

	def getRightTrigger(self):
		# TODO: Verify
		return self.js.get_axis(13)

