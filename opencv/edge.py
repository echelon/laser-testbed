#!/usr/bin/env python

import math
import cv2

cv2.namedWindow('capture')
cv2.namedWindow('cropped')
cv2.namedWindow('smooth')
#cv2.namedWindow('binary')
cv2.namedWindow('canny')
#cv2.namedWindow('erode')
#cv2.namedWindow('dilate')
cv2.namedWindow('out')

vc = cv2.VideoCapture(0)

# try to get the first frame
#if vc.isOpened():
#	rval, frame = vc.read()
#else:
#	rval = False

rval = True

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



	kern = 9
	smooth = gray
	smooth = cv2.GaussianBlur(gray, (kern, kern), 0)
	#smooth = cv2.GaussianBlur(smooth, (15,15), 0)


	thresh1 = 40.0 # HI -- 50 is great!
	thresh2 = thresh1 #- 15.0 # LOW -- 10 is good.
	canny = cv2.Canny(smooth, thresh1, thresh2)

	im = canny.copy()

	method = cv2.CHAIN_APPROX_NONE
	#method = cv2.CHAIN_APPROX_SIMPLE
	ctours, hier = cv2.findContours(im,
						method=method,
						mode=cv2.RETR_EXTERNAL)

	out = cropped.copy()
	for i in range(len(ctours)):
		if len(ctours[i]) < 5:
			continue
		cv2.drawContours(out, ctours, i, (255, 0, 0))

	cv2.imshow('capture', frame)
	cv2.imshow('cropped', cropped)
	cv2.imshow('smooth', smooth)
	cv2.imshow('canny', canny)
	#cv2.imshow('dilate', dilate)
	cv2.imshow('out', out)

	key = cv2.waitKey(20)
	if key == 27: # exit on ESC
		break

