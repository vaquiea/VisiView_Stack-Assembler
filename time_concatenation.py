# @File(label='Input directory', style='directory') import_dir
# @File(label='Output directory', style='directory') result_dir
# @String(label='Output file name', value='output.ome.tif') result_name

# @DatasetIOService io
# @OpService ops
# @StatusService status


import os
from glob import glob
from datetime import datetime

from java.lang import Long, Boolean, Short
from loci.formats import ImageReader, ImageWriter
from loci.formats import MetadataTools
from loci.formats import FormatTools
from loci.common import DataTools
from ome.xml.model.primitives import PositiveInteger
from ome.xml.model.enums import DimensionOrder
from ome.xml.model.enums import PixelType
from net.imagej.axis import Axes
from net.imglib2.view import Views


def copy(source, dimensions):
    target = ops.create().img(dimensions)
    ra = source.randomAccess()
    cu = target.localizingCursor()
    while cu.hasNext():
        cu.fwd()
        ra.setPosition(cu)
        cu.get().set(ra.get())

    return target


def run():
    t_start = datetime.now()
    image_paths = glob(os.path.join(str(import_dir.getPath()), '*tif'))

    print '\tread image metadata'
    reader = ImageReader()
    in_meta = MetadataTools.createOMEXMLMetadata()
    reader.setMetadataStore(in_meta)

    x_dims = []
    y_dims = []
    z_dims = []
    c_dims = []
    t_dims = []
    eff = []
    spp = []

    for image_path in image_paths:
        print '\t  parse %s' % (image_path)
        reader.setId(image_path)
        x_dims.append(reader.getSizeX())
        y_dims.append(reader.getSizeY())
        z_dims.append(reader.getSizeZ())
        c_dims.append(reader.getSizeC())
        t_dims.append(reader.getSizeT())
        eff.append(reader.imageCount / z_dims[-1] / t_dims[-1])
        spp.append(reader.getSizeC() / eff[-1])

    format = FormatTools.getPixelTypeString(reader.getPixelType())
    series = reader.getSeries()
    big_endian = Boolean.FALSE
    order = reader.getDimensionOrder()
    reader.close()

    # Compute the dimensions of the output file
    x_dim = max(x_dims)
    y_dim = max(y_dims)
    z_dim = max(z_dims)
    c_dim = max(c_dims)
    t_dim = max(t_dims)

    print '\t  series: %i' % series
    print '\t  format: %s' % format
    print '\t  dimension order: %s' % order
    print '\t  x: %s -> %i' % (x_dims, x_dim)
    print '\t  y: %s -> %i' % (y_dims, y_dim)
    print '\t  z: %s -> %i' % (z_dims, z_dim)
    print '\t  c: %s -> %i' % (c_dims, c_dim)
    print '\t  t: %s -> %i' % (t_dims, t_dim)
    print '\t  effective size c: %s' % eff
    print '\t  samples per pixel: %s' % spp

    # Get the time dimension from the number of input files
    t_dim = len(image_paths)

    # TODO: Tried to work out the order with Axes class, got something weird though.
    dimensions = [Short(x_dim), Short(y_dim), Short(c_dim), Short(z_dim)]

    pixels_per_plane = x_dim * y_dim

    # Assemble the metadata for the output file
    out_meta = MetadataTools.createOMEXMLMetadata()
    out_meta.setImageID(MetadataTools.createLSID('Image', series), series)
    out_meta.setPixelsID(MetadataTools.createLSID('Pixels', series), series)
    out_meta.setPixelsBinDataBigEndian(Boolean.TRUE, 0, 0)
    out_meta.setPixelsDimensionOrder(DimensionOrder.fromString(order), series)
    out_meta.setPixelsType(PixelType.fromString(format), series)
    out_meta.setPixelsSizeX(PositiveInteger(x_dim), series)
    out_meta.setPixelsSizeY(PositiveInteger(y_dim), series)
    out_meta.setPixelsSizeZ(PositiveInteger(z_dim), series)
    out_meta.setPixelsSizeC(PositiveInteger(c_dim), series)
    out_meta.setPixelsSizeT(PositiveInteger(t_dim), series)

    for c in range(c_dim):
        out_meta.setChannelID(MetadataTools.createLSID('Channel', series, c), series, c)
        out_meta.setChannelSamplesPerPixel(PositiveInteger(1), series, c);

    # Initialize the BF writer
    result_path = os.path.join(result_dir.getPath(), result_name)
    writer = ImageWriter()
    writer.setMetadataRetrieve(out_meta)
    writer.setId(result_path)
    print '\tcreated to %s' % (result_path)

    # Write the stacks into the output file
    N = len(image_paths)
    for i, image_path in enumerate(image_paths):
        status.showStatus(i, N, "catenating %i of %i time-points" % (i, N))
        print '\t  processing %s' % (image_path)
        ds = io.open(image_path)
        xi = ds.dimensionIndex(Axes.X)
        xv = ds.dimension(xi)
        yi = ds.dimensionIndex(Axes.Y)
        yv = ds.dimension(yi)
        zi = ds.dimensionIndex(Axes.Z)
        zv = ds.dimension(zi)
        ti = ds.dimensionIndex(Axes.TIME)
        tv = ds.dimension(ti)
        ci = ds.dimensionIndex(Axes.CHANNEL)
        cv = ds.dimension(ci)

        dx = float(x_dim - xv) / 2.0
        dy = float(y_dim - yv) / 2.0
        dz = float(z_dim - zv) / 2.0
        print '\t     translation vector (dx, dy, dz) = (%f, %f, %f)' % (dx, dy, dz)

        if (dx != 0) or (dy != 0) or (dz != 0):
            stk = Views.translate(ds, long(dx), long(dy), long(0), long(dz))
            stk = Views.extendZero(stk)
        else:
            stk = Views.extendZero(ds.getImgPlus().getImg())

        print '\t     writing planes ',
        n = 0
        plane = 1
        byte_array = []
        interval_view = Views.interval(stk, \
                                       [Long(0), Long(0), Long(0), Long(0)], \
                                       [Long(x_dim - 1), Long(y_dim - 1), Long(c_dim - 1), Long(z_dim - 1)])
        cursor = interval_view.cursor()
        while cursor.hasNext():
            n += 1
            cursor.fwd()
            value = cursor.get().getInteger()
            bytes = DataTools.shortToBytes(value, big_endian)
            byte_array.extend(bytes)

            if n == pixels_per_plane:
                writer.saveBytes(plane - 1, byte_array)

                print '.',
                if ((plane) % 10) == 0:
                    print '\n\t                    ',

                byte_array = []
                plane += 1
                n = 0

        print ' '

    writer.close()
    t = datetime.now() - t_start
    print '\twrote %i planes to %s in %i sec.' % (plane - 1, result_path, t.total_seconds())
    print '... done.'


if __name__ in ['__builtin__', '__main__']:
    status.clearStatus()
    print 'Running time_concatenation.py ...'
    run()
