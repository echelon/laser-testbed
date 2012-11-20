import math

def importObj(OBJECTS, MULT_X, MULT_Y):
	objCoords = [] # For building letters
	allCoords = [] # For recentering object

	for i in range(len(OBJECTS)):
		coords = OBJECTS[i]

		# Normalize/fix coordinate system
		for j in range(len(coords)):
			c = coords[j]
			x = math.floor(float(c['x'])*MULT_X)
			y = math.floor(float(c['y'])*MULT_Y)
			coords[j] = {'x': x, 'y': y}

		#if random.randint(0, 1) == 0:
		#	continue

		OBJECTS[i] = coords
		objCoords.append(coords)
		allCoords.extend(coords)

	# Normalize coordinate system!
	xsum = 0
	ysum = 0
	for c in allCoords:
		xsum += c['x']
		ysum += c['y']

	xavg = xsum / len(allCoords)
	yavg = ysum / len(allCoords)

	for i in range(len(objCoords)):
		for j in range(len(objCoords[i])):
			objCoords[i][j]['x'] -= xavg
			objCoords[i][j]['y'] -= yavg

	return objCoords
