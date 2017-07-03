# @File(label="Input directory", style="directory") input_dir
# @File(label="Output directory", style="directory") output_dir
# @String(label="Image file extension", value=".tif") extension
# @String(label="Channel minima separated by ; (-1 -> auto)") ch_min
# @String(label="Channel maxima separated by ; (-1 -> auto)") ch_max


import os
from glob import glob
from ij import IJ
from java.lang import Double


def run(in_dir, ou_dir, extension, minimum, maximum):
	extension = extension.strip()
	extension = "*" + extension
		
	for path in glob(os.path.join(in_dir, '*.tif')):
		print path + ':',
		IJ.open(path)
		imp = IJ.getImage()
		minima = [x.strip() for x in ch_min.split(';')]
		maxima = [x.strip() for x in ch_max.split(';')]
		for c in range(0, imp.getNChannels()):
			imp.setC(c+1)
			ip = imp.getProcessor()
			stats = ip.getStats()
			M = 2**ip.getBitDepth()			
			if minima[c] == '-1':
				mi = stats.min
			else:
				mi = Double.parseDouble(minima[c])
			if maxima[c] == '-1':
				ma = stats.max
			else:
				ma = Double.parseDouble(maxima[c])
			scale = M / (ma - mi)
			ip.subtract(mi)
			ip.multiply(scale)
			print ' ch' + str(c) + '=[' + str(mi) + ' ... ' + str(ma) + ']', 
			
		print ' '
		IJ.run('Make Composite');
		IJ.run('RGB Color')
		IJ.run('Save', 'save=[' + os.path.join(ou_dir, os.path.basename(path)) + ']')
		IJ.run('Close All');


if __name__ in ['__builtin__', '__main__']:
	run(input_dir.getPath(), output_dir.getPath(), extension, ch_min, ch_max)
