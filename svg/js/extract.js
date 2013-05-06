/**
 * This is very, very, very ugly, but it enables us to extract 
 * points from SVG to give to Python.
 */

var extract = function()
{
	var $paths = $('path');
	var $svg = $('svg');
	var svg = $svg[0];
	var paths = svg.getElementsByTagName('path');

	var skip = [];

	// Extract points for all paths.
	var objects = [];
	console.log("Num Svg Paths: ", paths.length);

	// Get samplePts from a path
	var getPathPoints = function(path, numSamplePts) {
		var pts = [],
			pt = null,
			len = path.getTotalLength(),
			i = 0;

		for(i = 0; i < numSamplePts; i++) {
			pt = path.getPointAtLength((i/numSamplePts)*len);
			pts.push(pt.x);
			pts.push(pt.y);
		}
		return pts;
	}

	var pts = null; 


	/*for(var i = 0; i < paths.length; i++) {
		//if(i in skip) {
		//	continue;
		//}
		
		if( i > paths.length / 2 - 1) {
			break;
		}
		//switch(i) {
		//	case 0:
		//		SAMPLE = 100;
		//		break;
		//	default:
		//		break;
		//}

		pts = getPathPoints(paths[i], 500);
		objects.push(pts);
	}*/

	var i = 0;

	objects.push(getPathPoints(paths[0], 300));  // outline
	objects.push(getPathPoints(paths[1], 100)); //face
	objects.push(getPathPoints(paths[2], 200)); // eyes
	objects.push(getPathPoints(paths[3], 100));
	objects.push(getPathPoints(paths[4], 50)); // mouth


	/*pts = getPathPoints(paths[0], 4000);
	objects.push(pts);
	pts = getPathPoints(paths[1], 40);
	objects.push(pts);
	pts = getPathPoints(paths[2], 40);
	objects.push(pts);
	pts = getPathPoints(paths[3], 40);
	objects.push(pts);*/

	return objects;
}

var format = function(objects)
{
	// Export as string for Python
	var str = "OBJECTS = [\n";
	for(var i = 0; i < objects.length; i++) {
		var obj = objects[i];
		str += "\n\n\t# OBJECT ";
		str += "\n\t[";
		for(var j = 0; j < obj.length/2; j++) {
			var z = j*2;
			var x = obj[z];
			var y = obj[z+1];
			str += "\n\t\t{'x': " + x + ", 'y': " + y + "},";
		}
		str += "\n\t],";
	}
	str += "\n]";
	return str;
}

var main = function()
{
	var objs = extract();
	var str = format(objs);

	var $paths = $('path');
	var $svg = $('svg');
	var svg = $svg[0];
	var paths = svg.getElementsByTagName('path');

	$svg.hide();
	var $body = $('body');
	var $text = $('<textarea>').css({
		width: '100%',
		height: '900px',
	});
	$body.html($text);
	$('textarea').html(str).focus().select();

	return;
}
