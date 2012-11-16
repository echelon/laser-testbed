#!/usr/bin/env python
# Audio Analysis Code is from:
# http://www.swharden.com/blog/2010-03-05-realtime-
# fft-graph-of-audio-wav-file-or-microphone-input-
# with-python-scipy-and-wckgraph/ 

import os
import math
import random
import cv2
import itertools
import sys
import time
import thread
import threading

import numpy as np
import pyaudio
import scipy
import struct
import scipy.fftpack

from pylab import *

from lib import dac
from lib.common import *
from lib.stream import PointStream
from lib.shape import Shape

#from pyfmodex import *
import pyfmodex

bufferSize=2**11
sampleRate=48100
#sampleRate=64000

AVERAGE = 0.0
MAX = 0.0
FFTY = [0.0]*10

chunks = []
ffts = []

def stream():
	global bufferSize, chunks

	p = pyaudio.PyAudio()

	inStream = p.open(format=pyaudio.paInt16,channels=1,\
					rate=sampleRate,input=True,
					frames_per_buffer=bufferSize)

	while True:
		chunks.append(inStream.read(bufferSize))
		time.sleep(0.1)

def graph():
	global AVERAGE, MAX, FFTY
	global chunks, bufferSize, fftx,ffty

	if len(chunks) > 0:
		data = chunks.pop(0)
		data = scipy.array(struct.unpack("%dB"%(bufferSize*2),data))

		MX = max(data)
		AVG = np.mean(data)

		#print MX, AVG

		ffty = scipy.fftpack.fft(data)
		#fftx = scipy.fftpack.rfftfreq(bufferSize*2, 1.0/sampleRate)
		#fftx = fftx[0:len(fftx)/4]
		ffty = abs(ffty[0:len(ffty)/2])/1000
		#ffty1 = ffty[:len(ffty)/2]
		#ffty2 = ffty[len(ffty)/2::]+2
		#ffty2 = ffty2[::-1]

		#ffty=ffty1+ffty2
		ffty=scipy.log(ffty)-2	


		#ffty = ffty[:100] + ffty[len(ffty)-100:]

		srt = list(ffty[:])

		srt.sort(reverse=True)
		ffty = srt[1:100]
		#ffty = srt[:10]
		#print sort[:10]

		FFTY = srt

		#plot(range(len(ffty)), ffty)
		#show()

		AVERAGE = np.mean(ffty)
		STDEV = np.std(ffty)
		MAX = max(ffty)
		MIN = min(ffty)
		RNG = MAX - MIN
		#MAX = STDEV

        if len(chunks)>20:
			print "falling behind...",len(chunks)
			chunks = []

"""
def go(x=None):
	global fftx,ffty
	print "STARTING!"
	threading.Thread(target=record).start()
	while True:
		graph()

go()
mainloop()
"""

"""
CONFIGURATION
"""

LASER_POWER_DENOM = 1.0

ORIGIN_X = 0
ORIGIN_Y = 6000

COLOR_R = CMAX / 1
COLOR_G = CMAX / 1
COLOR_B = CMAX / 1

WAVE_SAMPLE_PTS = 500
WAVE_PERIODS = 4
WAVE_RATE = 1.1
WAVE_WIDTH = 42000 # XXX Not wavelength!
WAVE_AMPLITUDE_MAGNITUDE = 15000 # dither between +/-
WAVE_AMPLITUDE_RATE = 900

"""
CODE BEGINS HERE
"""

class SineWave(Shape):

	def __init__(self, x = 0, y = 0, r = 0, g = 0, b = 0,
			width = 10000, height = 2200):

		super(SineWave, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.theta = 0
		self.thetaRate = 0

		self.height = height
		self.width = width

		self.sineAmp = 2000
		self.sinePos = 0
		self.numPeriods = 4

	def produce(self):
		"""
		Generate the points of the circle.
		"""
		r, g, b = (0, 0, 0)

		# Generate points
		lx = - self.width / 2

		rh = self.r / 8
		bh = self.b / 8

		for i in xrange(0, WAVE_SAMPLE_PTS, 1):
			periods = self.numPeriods * 2 * math.pi
			percent = float(i) / WAVE_SAMPLE_PTS

			x = lx + int(self.width* percent) + self.x
			i = (percent * periods) + self.sinePos
			y = int(math.sin(i) * self.sineAmp) + self.y

			# XXX FIX MATHS: Something wrong, 
			# but does it matter?
			r = int(abs(math.floor(self.g -
						rh*percent)))
			g = abs(self.g)
			b = int(abs(math.floor(self.b -
						bh + bh*percent)))

			s = (x, y, r, g, b)
			if s[0] == 0 or s[1] == 0:
				continue # XXX DEBUG
			yield s

		self.drawn = True

def dac_thread():
	global SINEW
	global WAVE_PERIODS

	ps = PointStream()
	#ps.showTracking = True
	#ps.showBlanking = True
	ps.trackingSamplePts = 50
	ps.blankingSamplePts = 50

	SINEW = SineWave(0, 0, COLOR_R/LASER_POWER_DENOM,
							COLOR_G/LASER_POWER_DENOM,
							COLOR_B/LASER_POWER_DENOM)

	SINEW.numPeriods = WAVE_PERIODS
	SINEW.width = WAVE_WIDTH
	SINEW.sineAmp = WAVE_AMPLITUDE_MAGNITUDE

	SINEW.x = ORIGIN_X
	SINEW.y = ORIGIN_Y

	#SQUARE.x = SQUARE_X
	#SQUARE.y = SQUARE_Y

	ps.objects.append(SINEW)

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
			pass

def animate_thread():
	global SINEW
	global AVERAGE, MAX, FFTY

	inc = True
	panInc = True

	xPan = 0
	spin = 0

	ampDirec = 1

	threading.Thread(target=stream).start()

	while True:
		# Translation rate animation
		"""
		SINEW.sinePos += WAVE_RATE
		time.sleep(0.015)

		#  Amplitude shift animation
		if SINEW.sineAmp > \
				WAVE_AMPLITUDE_MAGNITUDE:
			ampDirec = -1
		elif SINEW.sineAmp < \
				-WAVE_AMPLITUDE_MAGNITUDE:
			ampDirec = 1
		if ampDirec >= 0:
			SINEW.sineAmp += WAVE_AMPLITUDE_RATE
		else:
			SINEW.sineAmp -= WAVE_AMPLITUDE_RATE
		"""

		graph()

		y = np.std(FFTY[1:5])

		print y

		##print "Mean: %f" % y

		# Clamp value to [-3, 3]
		y = max(min(y, 3.0), -3.0)

		# Normalize to [-1, 1]
		y /= 3.0

		#print y

		amp = (y*10)**3
		amp *= 10

		#print amp

		SINEW.sinePos += WAVE_RATE
		SINEW.sineAmp = amp

		time.sleep(0.1)
		pass

def color_thread():
	global SINEW

	rr = DitherColor(inc = random.randint(500, 5000))
	gg = DitherColor(inc = random.randint(500, 5000))
	bb = DitherColor(inc = random.randint(500, 5000))

	# Unfortunately, my red laser is out of commission
	rr.min = CMAX - 1
	rr.max = CMAX
	gg.min = CMAX / 2
	gg.max = CMAX
	bb.min = CMAX / 3
	bb.max = CMAX

	color = RandomColorAnimation()

	while True:
		rr.incr()
		gg.incr()
		bb.incr()
		color.frame()

		#SINEW.r = color.curColor.r
		#SINEW.g = color.curColor.g
		#SINEW.b = color.curColor.b

		SINEW.r = int(rr.getVal())
		SINEW.g = int(gg.getVal())
		SINEW.b = int(bb.getVal())

		time.sleep(0.1)

#
# Start Threads
#

SINEW = SineWave()

thread.start_new_thread(dac_thread, ())
time.sleep(1.0)
thread.start_new_thread(animate_thread, ())
#thread.start_new_thread(color_thread, ())


while True:
	time.sleep(100000)









"""
def main():
	print dir(pyfmodex)
	system = pyfmodex.System()
	system.init()

	fname = "/home/brandon/Music/Starfucker" + \
			"/Reptilians/02 Julius.mp3"
	snd1 = system.create_sound(fname)

	print fname
	print snd1
	print dir(snd1)
	#snd1.play()
	print "==============="
	print dir(system)
	system.get_spectrum()
            system.getSpectrum(spectrum, 512, count, FMOD.DSP_FFT_WINDOW.TRIANGLE);

	time.sleep(5350)
"""

