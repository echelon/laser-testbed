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

	// Extract points for all paths.
	var objects = [];
	for(var i = 0; i < paths.length; i++) {
		var p = paths[i];
		var pts = [];
		for(var j = 0; j < 70; j++) {
			var z = j*20;
			var pt = p.getPointAtLength(z);
			pts.push(pt.x);
			pts.push(pt.y);
		}
		objects.push(pts);
	}
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
	$body.html(str);

	return;
}
