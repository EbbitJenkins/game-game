#!/usr/bin/env python

import sys, struct, os, itertools, base64, string
import xml.etree.ElementTree as etree
from gzip import GzipFile
from cStringIO import StringIO

def convert(filename):
    infile = etree.parse(filename)

    # Get and sanity check attributes in the top-level <map> element
    attrib = infile.getroot().attrib
    assert(attrib["orientation"] == "orthogonal")
    assert(attrib["version"] == "0.99b")
    width = int(attrib["width"])
    height = int(attrib["height"])

    # The first (and for now the only) tileset is the real tileset used by
    # the game. Get image filename, tile size, and the global tile id for
    # the first tile in the tileset.
    tileset = infile.find("tileset")
    attrib = tileset.attrib
    firstgid = int(attrib["firstgid"])
    tilewidth = int(attrib["tilewidth"])
    tileheight = int(attrib["tileheight"])
    tilefile = tileset.find("image").attrib["source"]

    # The first (bottom most) layer is the visible background tile layer.
    # Convert the base64 encoded data into binary
    data = infile.find("layer/data")
    attrib = data.attrib
    assert(attrib["encoding"] == "base64")
    bindata = base64.b64decode(data.text)

    # Decompress binary data if it is Gzip compressed, and from now on access
    # the raw data as an in memory file object. If the data is not compressed
    # then wrap the raw data in a dummy file object for uniformity.
    if "compression" in attrib:
        assert(attrib["compression"] == "gzip")
        rawdata = GzipFile(mode="r", fileobj=StringIO(bindata))
    else:
        rawdata = StringIO(bindata)

    # The raw binary data for a layer is an array of 32bit little-endian
    # integers. Each integer is the global tile id for that location.
    # Create a generator that will unpack the raw data one row at a time
    # returning a sequence of tuples of numbers with each tuple containing
    # the global tile id numbers for that row.
    format = "<%di" % width
    count = struct.calcsize(format)
    tiles=[ struct.unpack(format, rawdata.read(count)) for i in xrange(height) ]

    # Create the output ASCII map file
    filename = os.path.splitext(filename)[0] + ".level"
    outfile = open(filename, "w")

    # Print the tileset name, tile set size, and map size
    print >> outfile, tilefile, tilewidth, tileheight,
    print >> outfile, tilewidth * width, tileheight * height
    print >> outfile

    # Print the map as a grid of ASCII numbers, converting each global tile id
    # to a 0 based "tileset relative" id. Each tile set id is "pretty printed"
    # as a 3 digit number with leading zeroes.
    for row in tiles:
        f = lambda id: "%03d" % (id - firstgid if id >= firstgid else id)
        row = itertools.imap(f, row)
        print >> outfile, string.join(row)

    # Print dummy boundary layer
    print >> outfile
    for row in tiles:
        print >> outfile, ". " * len(row)

    outfile.close()

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print "Usage: %s input.level" % sys.argv[0]
        sys.exit()

    convert(sys.argv[1])
