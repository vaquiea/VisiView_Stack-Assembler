# @File(label='Input directory', style='directory') input_dir
# @String(label='Input file extension', value='.stk') extension
# @File(label='Output directory', style='directory') output_dir
# @String (label='Channel patterns separated by semicolon', value='mCherry;GFP') patterns
# @String(label='File naming (mapping)', value='None', choices={'None', 'Sequential', 's -> y', 's -> x'}) mapping
# @Boolean (label='Arrange output images in time-sub-directories', value=True) subdirs

# @LogService log


import os, re
from glob import glob
from ij import IJ, WindowManager, ImagePlus, ImageStack, CompositeImage
from ij.io import FileSaver


def run():
    target_dir = output_dir.getPath()
    
    log.info('Running merge_stacks.py')
    log.info('\tInput directory: %s' % input_dir)
    log.info('\tOutput directory %s' % output_dir)

    # Get the files
    ch = {}
    for pattern in patterns.split(";"):
        ch[pattern] = glob(os.path.join(input_dir.getPath(), "*" + pattern + "*" + extension))
        ch[pattern].sort()  # Sort the file names to make sure from the channels come in the same order.

    keys = ch.keys()
    channels = len(keys)

    # Sanity checks
    if channels < 2:
        log.error('\tFound only one channel, nothing to merge. Put at least two channel patterns separated by semicolon.')
        return

    n = 0
    for p in range(channels - 1):
        n = len(ch[keys[p]])
        if n != len(ch[keys[p + 1]]):
            log.error('The number of file for both channels have to be the same. found %i and %i.' % (nch1, nch2))
            return

    log.info('\tMerging %i image sets:' % n)
    for i in range(n):

        msg = '\t'
        fn = {}
        # Separate path and file name
        for pattern in keys:
            fn[pattern] = os.path.basename(ch[pattern][i])
            msg += fn[pattern] + ', '

        log.info(msg[:-2])

        # extract experiment name from the filename
        experiment = fn[keys[0]].split('_')[0]
        merge_name = experiment + '_'

        # extract fieldnumber from the file name
        if mapping == 'None':
            merge_name = fn[keys[0]].replace(extension, '')
            for pattern in keys:
                for part in pattern.split('*'):
                    merge_name = merge_name.replace(part, '')
        elif mapping == 'Sequential':
            merge_name += '%03d' % i
        elif 's ->' in mapping:
            match = re.search('.*_s(\d{1,2})_.*', fn[keys[0]])
            if match:
                if mapping == 's -> y':
                    merge_name += 'x1_y%s' % match.group(1)
                elif mapping == 's -> x':
                    merge_name += 'x%s_y1' % match.group(1)
            else:
                log.error('\tCould not extract the field number from the file name. Consider using no mapping (None).')
                return

        # extract time-point number from the file name
        match = re.search('.*_t(\d{1,2})\.[A-Za-z0-9]{3}$', fn[keys[0]])
        if match and (mapping != 'None'):
            time = match.group(1)
            time_dir_name = 't%02d' % (int(time))
            merge_name += '_t%02d' % int(time)
            if subdirs:
                target_dir = os.path.join(output_dir.getPath(), time_dir_name)
                if not os.path.exists(target_dir):
                    os.mkdir(target_dir)

        # Merge stacks
        output_file = os.path.join(target_dir, merge_name + '.tif')
        if os.path.exists(output_file):
            log.info('\t\talready processed: %s' % output_file)
        else:
            imps = {}
            for pattern in keys:
                imps[pattern] = IJ.openImage(ch[pattern][i])

            slices = imps[keys[0]].getNSlices()
            width = imps[keys[0]].getWidth()
            height = imps[keys[0]].getHeight()

            # Create the new image
            stk = ImageStack(width, height)
            for slice in range(1, slices + 1):
                for channel, pattern in enumerate(keys):
                    channel += 1  # enumeration from 1
                    imps[pattern].setPosition(channel, slice, 1)
                    stk.addSlice(None, imps[pattern].getProcessor())

            imp = ImagePlus(merge_name, stk)
            imp.setDimensions(channels, slices, 1)
            comp = CompositeImage(imp, CompositeImage.COLOR)
            #            comp.show()
            saver = FileSaver(comp)
            saver.saveAsTiff(output_file)

            log.info('\t\tsaving:  %s' % (output_file))

    log.info('\tDone.')


if __name__ in ['__builtin__', '__main__']:
    IJ.run("Console", "uiservice=[org.scijava.ui.DefaultUIService [priority = 0.0]]")
    run()
