# @File(label='Choose the directory containing the .stk-files', style='directory') inputDir
# @String(label='File name pattern channel 1', value='*GFP*stk') pattern_ch1
# @String(label='File name pattern channel 2', value='*mCherry*stk') pattern_ch2


import os
from time import sleep
from glob import glob
from ij import IJ, WindowManager
from ij.io import DirectoryChooser


def run():
	print 'Running time-point stitching'
	print 'Working directory: %s' % (inputDir)

	# Get the files
	ch1 = glob(os.path.join(inputDir.getPath(), pattern_ch1))
	ch2 = glob(os.path.join(inputDir.getPath(), pattern_ch2))
	nch1 = len(ch1)
	nch2 = len(ch2)
	
	if nch1 % 2 == 1:
		print 'The number of files for channel 1 (%i) should be pair (as in pairwise stitching).' % nch1
		return
		
	if (nch2 % 2) == 1:
		print 'The number of files for channel 2 (%i) should be pair(as in pairwise stitching).' % nch2
		return

	if nch1 != nch2:
		print 'The number of file for both channels have to be the same. found %i and %i.' % (nch1, nch2)
		return

	# Sort the file names to make sure the corresponding files from the channels come in the 
	# desired order.
	ch1.sort()
	ch2.sort()

	print 'Merging:'
	for item1, item2 in zip(ch1, ch2):
		# Extract file name information and create an output file name with x-y grid coordinates
		fn1 = os.path.basename(item1)
		fn2 = os.path.basename(item2)
		experiment, _, field, time = fn2[:-4].split('_')
		merge_name = '%s_x1_y%s_t%02d' % (experiment, field[1:], int(time[1:]))
		
		# Create an output directory per time-point
		time_dir_name = 't%02d' % (int(time[1:]))
		output_dir = os.path.join(inputDir.getPath(), time_dir_name)
		if os.path.exists(output_dir):
			pass
#			print '\t\toutput directory %s already exists' % output_dir
		else:
			os.mkdir(output_dir)
		
		print '\t%s and %s' % (fn1, fn2)

		output_file = os.path.join(output_dir, merge_name + '.tif')
		if os.path.exists(output_file):
			print '\t\talready processed'
		else:
			IJ.open(os.path.join(inputDir, item1))
			IJ.open(os.path.join(inputDir, item2))
			
			IJ.run('Merge Channels...', 'c1=' + fn1 + ' c2=' + fn2 + ' create')
			sleep(1)
			imp = WindowManager.getImage('Composite')
			imp.setTitle(merge_name)
			imp.updateAndRepaintWindow()
							
			IJ.save(imp, output_file)
			print '\t\tsaving:  %s' % (output_file)
		IJ.run('Close All')
	
	print ('Done.')
			
			
if __name__ == '__main__':
	run()
