#!/usr/bin/env python

import os
import math
import cv2
import itertools
import sys
import time
import thread

from lib import dac
from lib.common import *
from lib.stream import PointStream
from lib.shape import Shape


"""
CONFIGURATION
"""

LASER_POWER_DENOM = 1.0

"""
Globals
"""

objs = []
obj = None
ps = None


"""
Animation code / logic
"""

class Contours(Shape):

	def __init__(self, x = 0, y = 0,
			r = 0, g = 0, b = 0):
		super(Contours, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.theta = 0
		self.thetaRate = 0

		self.vc = cv2.VideoCapture(0)



	def produce(self):
		"""
		Generate the points of the circle.
		"""
		r, g, b = (0, 0, 0)

		rval, frame = self.vc.read()

		gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
		smooth = cv2.GaussianBlur(gray, (7,7), 0)

		binary = cv2.adaptiveThreshold(smooth, 255,
					cv2.ADAPTIVE_THRESH_MEAN_C,
					cv2.THRESH_BINARY, 3, 0)

		kern = cv2.getStructuringElement(
					cv2.MORPH_CROSS, (3,3))
		erode = cv2.erode(binary, kern)

		im = erode.copy()
		ctours, hier = cv2.findContours(im,
							method=cv2.CHAIN_APPROX_NONE,
							mode=cv2.RETR_EXTERNAL)

		for c in ctours:
			for d in c:
				for e in d:
					x = e[0] * 10
					y = e[1] * 10
					yield (x, y, CMAX, CMAX, CMAX)


		self.drawn = True


def dac_thread():
	global objs
	global ps

	ps.objects.append(obj)

	while True:
		try:
			d = dac.DAC(dac.find_first_dac())
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

#
# Start Threads
#

def main():
	global obj
	global ps

	obj = Contours()
	ps = PointStream()
	#ps.showBlanking = True
	#ps.showTracking = True
	ps.blankingSamplePts = 10
	ps.trackingSamplePts = 10

	thread.start_new_thread(dac_thread, ())
	time.sleep(1.0)
	#thread.start_new_thread(spin_thread, ())

	while True:
		time.sleep(100000)

if __name__ == '__main__':
	main()
