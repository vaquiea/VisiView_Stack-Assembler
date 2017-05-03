# VisiView Stack-Assembler
This is a collection of [ImageJ][imagej] python scripts to assemble the multi-dimensional light microscopy images acquired with the spinning disk confocal [CSU-W1][csu-w1] into a single image-file.

# Installation
Stable versions of the scripts can be downloaded from the [release-page][release].
After download and extraction of the scripts, they can be opened with ImageJ via Menu > File > Open, or simply by drag and dropping the files on the main window of the ImageJ user interface. Once the scripts appeared in the script editor, they can be executed with the "Run" button. To install the macros in ImageJ and to learn more about scripting please refer to the [Jython Scripting][jython] page on the Imagej-Wiki.

# Workflow
The raw images from the microscope need to be assembeled in a multi-dimensional stack for further analysis. The stk-files produced by the microscope represent imaged volumes (x, y and z spacial dimensions). These need first to be merged (channels/colors). Then the multiple fields of view need to be stiched together to form one single mult-color volume. The final step consists in assembling the time-points. The resulting hyperstacks then have x, y, z spacial dimensions plus color (c) plus time (t). The entire assembling workflow consists in executing the scripts in the following order:

1. merge_stack.py will create a multi-color hyperstack from the monochrome image stacks, resulting in x-y-z-c-hyperstacks.
2. stick_x-y-stacks.py will stich the multiple fields of view together to one spacially continous volume.
3. time_concatenation.py will assemble the stiched x-y-z-c-hyperstacks to x-y-z-c-t-hypterstacks (multicolor movies of imaged volumes).

[imagej]: http://imagej.net
[jython]: http://imagej.net/Jython_Scripting
[csu-w1]: http://www.visitron.de/Products/Confocal/CSU_W1/csu_w1.html
[release]: https://github.com/vaquiea/VisiView_Stack-Assembler/releases