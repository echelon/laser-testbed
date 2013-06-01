#!/usr/bin/env python

"""
Not an exact science. Lots of trial and error.
"""

import math
import sys
import cv2

def noop(*arg):
	pass

#cv2.namedWindow('capture')
cv2.namedWindow('cropped')

cv2.namedWindow('smooth')
cv2.createTrackbar('kernel', 'smooth', 0, 21, noop)

cv2.namedWindow('canny')
cv2.createTrackbar('threshLo', 'canny', 0, 130, noop)
cv2.createTrackbar('threshHi', 'canny', 0, 130, noop)

cv2.namedWindow('morph')
cv2.namedWindow('morph2')
cv2.namedWindow('thresh')
#cv2.namedWindow('erode')
#cv2.namedWindow('dilate')
cv2.namedWindow('out')



vc = cv2.VideoCapture(0)

# try to get the first frame
#if vc.isOpened():
#	rval, frame = vc.read()
#else:
#	rval = False

while False:

	"""binary = cv2.adaptiveThreshold(smooth, 255,
				cv2.ADAPTIVE_THRESH_MEAN_C,
				cv2.THRESH_BINARY, 5, 0)
	"""

	# morph_erode, morph_...
	#kern = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
	#kern = cv2.getStructuringElement(cv2.MORPH_CROSS, (5,5))
	#erode = cv2.erode(binary, kern)
	#dilate = cv2.dilate(canny, kern)
	#dilate = cv2.erode(dilate, kern)
	#im = morph.copy()

	"""
	rho = 1
	theta = math.pi / 180
	thresh = 100
	lines = cv2.HoughLinesP(gray, rho, theta, thresh)
	for l in lines[-1]:
		p1 = (l[0], l[1])
		p2 = (l[2], l[3])
		cv2.line(gray, p1, p2, (0, 0, 0))
		#cv2.line(gray, p1, p2, (0,0,255), 3)
	#print lines
	#print "========="
	"""

rval = True

while rval:
	rval, frame = vc.read()

	width = 400
	height = 400
	x1 = 150
	y1 = 70
	x2 = x1 + width
	y2 = y1 + height

	cropped = frame[y1:y2, x1:x2]

	gray = cv2.cvtColor(cropped, cv2.COLOR_RGB2GRAY)

	smooth = gray

	kern = 3
	k = cv2.getTrackbarPos('kernel', 'smooth')
	if k % 2 != 1:
		k += 1
	if k > 3 and k % 2 == 1:
		kern = k

	smooth = cv2.GaussianBlur(gray, (kern, kern), 0)


	"""
	ret, thresh = cv2.threshold(smooth, 100, 255, cv2.THRESH_BINARY)
	"""
	thresh = cv2.adaptiveThreshold(
			src=smooth,
			maxValue=255,
			adaptiveMethod=cv2.ADAPTIVE_THRESH_MEAN_C,
			thresholdType=cv2.THRESH_BINARY,
			blockSize=15,
			C=3)

	threshLo = 40.0 # HI -- 50 is great!
	threshHi = 30.0 #- 15.0 # LOW -- 10 is good.

	threshLo = cv2.getTrackbarPos('threshLo', 'canny')
	threshHi = cv2.getTrackbarPos('threshHi', 'canny')
	canny = cv2.Canny(smooth, threshLo, threshHi)

	def kernel(size, shape):
		size = (size, size)
		if shape.lower() in ['r', 'rect']:
			shape = cv2.MORPH_RECT
		elif shape.lower() in ['c', 'cross']:
			shape = cv2.MORPH_CROSS
		elif shape.lower() in ['e', 'ellipse']:
			shape = cv2.MORPH_ELLIPSE
		return cv2.getStructuringElement(shape, size)

	morph = cv2.dilate(canny, kernel=kernel(3, 'e'))
	morph2 = cv2.dilate(canny, kernel=kernel(3, 'c'))

	im = canny.copy()

	mode = cv2.RETR_EXTERNAL
	#mode = cv2.RETR_LIST
	method = cv2.CHAIN_APPROX_NONE
	#method = cv2.CHAIN_APPROX_TC89_KCOS
	#method = cv2.CHAIN_APPROX_TC89_L1
	#method = cv2.CHAIN_APPROX_SIMPLE

	ctours, hier = cv2.findContours(im, method=method, mode=mode)

	print "# Contours = %d" % len(ctours)

	out = cropped.copy()
	out.fill(0)
	#out = cv2.createImage((width, height), 8, 3)
	for i in range(len(ctours)):
		if len(ctours[i]) < 20:
			continue
		cv2.drawContours(out, ctours, i, (255, 0, 0))


	#cv2.imshow('capture', frame)
	cv2.imshow('cropped', cropped)
	cv2.imshow('smooth', smooth)
	cv2.imshow('thresh', thresh)
	cv2.imshow('morph', morph)
	cv2.imshow('morph2', morph2)
	cv2.imshow('canny', canny)
	#cv2.imshow('dilate', dilate)
	cv2.imshow('out', out)

	key = cv2.waitKey(20)
	if key == 27: # exit on ESC
		break

