# @File(label='Input directory (containing time-point subdirectories)', style='directory') input_dir
# @Integer(label='Image overlap', value=20) overlap
# @String(label='Memory management', choices={'Save computation time (but use more RAM)', 'Save memory (but slower)'}, value='Save computation time (but use more RAM)') memory

# @LogService log


import os
import re
from glob import glob
from ij import IJ, WindowManager


def run():
    time_dirs = glob(os.path.join(input_dir.getPath(), 't*/'))

    for time_dir in time_dirs:
        log.info('\tprocessing %s' % time_dir)

        # Extract information from file name
        xy_files = glob(os.path.join(time_dir, '*.tif'))
        match = re.search('(.*)_x\d_y\d_t(\d{1,2})\.tif', os.path.basename(xy_files[0]))
        if not match:
            log.error('\tCould not extract time digits from %s\nAbort.' % (time_dir))
            return

        experiment = match.group(1)
        time = match.group(2)
        fields = str(len(xy_files))
        log.info('\t\texperiment=%s, time-point=%s, #files=%s' % (experiment, time, fields))

        # Compose the output file name
        output_file = os.path.join(input_dir.getPath(), experiment + '_t' + time + '.tif')
        if os.path.exists(output_file):
            log.info('\t\talreday stitched: %s)' % output_file)
            continue

        # Run the stitching macro
        print '\t\truning stitching plugin...'
        IJ.run('Grid/Collection stitching', \
               'type=[Filename defined position]' + \
               ' order=[Defined by filename         ]' + \
               ' grid_size_x=1' + \
               ' grid_size_y=' + fields + \
               ' tile_overlap=' + str(overlap) + \
               ' first_file_index_x=1' + \
               ' first_file_index_y=1' + \
               ' directory=' + time_dir + \
               ' file_names=12_x{x}_y{y}_t' + time + '.tif' + \
               ' output_textfile_name=TileConfiguration.txt' + \
               ' fusion_method=[Linear Blending]' + \
               ' regression_threshold=0.30' + \
               ' max/avg_displacement_threshold=2.50' + \
               ' absolute_displacement_threshold=3.50' + \
               ' compute_overlap' + \
               ' subpixel_accuracy' + \
               ' computation_parameters=[Save computation time (but use more RAM)]' + \
               ' image_output=[Fuse and display]');

        # Save the output
        imp = WindowManager.getImage("Fused")
        IJ.save(imp, output_file)
        log.info('\t\tsaved:  %s' % (output_file))
        IJ.run('Close All')

    log.info('Done.')


if __name__ in ['__builtin__', '__main__']:
    IJ.run("Console", "uiservice=[org.scijava.ui.DefaultUIService [priority = 0.0]]")
    log.info('Running "stitch_x-y-stacks.py" macro')
    run()
