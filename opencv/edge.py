#!/usr/bin/env python

import math
import cv2

cv2.namedWindow('capture')
cv2.namedWindow('smooth')
cv2.namedWindow('binary')
cv2.namedWindow('erode')
cv2.namedWindow('dilate')
cv2.namedWindow('morph')

vc = cv2.VideoCapture(0)

# try to get the first frame
#if vc.isOpened():
#	rval, frame = vc.read()
#else:
#	rval = False

rval = True

while rval:
	#cv2.imshow("capture", frame)
	rval, frame = vc.read()

	gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

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

	smooth = gray
	smooth = cv2.GaussianBlur(gray, (15,15), 0)
	#smooth = cv2.GaussianBlur(smooth, (15,15), 0)

	binary = cv2.adaptiveThreshold(smooth, 255,
				cv2.ADAPTIVE_THRESH_MEAN_C,
				cv2.THRESH_BINARY, 5, 0)

	# morph_erode, morph_...
	#kern = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
	kern = cv2.getStructuringElement(cv2.MORPH_CROSS, (5,5))
	erode = cv2.erode(binary, kern)
	dilate = cv2.dilate(binary, kern)
	morph = cv2.dilate(erode, kern)



	im = morph.copy()

	ctours, hier = cv2.findContours(im,
						method=cv2.CHAIN_APPROX_NONE,
						mode=cv2.RETR_EXTERNAL)

	out = frame.copy()
	for i in range(len(ctours)):
		if len(ctours[i]) < 50:
			continue
		cv2.drawContours(out, ctours, i, (255, 0, 0))

	cv2.imshow('capture', frame)
	cv2.imshow('smooth', smooth)
	cv2.imshow('binary', binary)
	cv2.imshow('erode', erode)
	cv2.imshow('dilate', dilate)
	cv2.imshow('morph', morph)
	cv2.imshow('out', out)

	key = cv2.waitKey(20)
	if key == 27: # exit on ESC
		break

