#!/usr/bin/env python

import sys, struct, os, itertools, base64, gzip
from gzip import GzipFile
from cStringIO import StringIO

def convert(filename):
    # Load the ASCII map file; for now don't handle boundry data
    tileset_str, tile_str, coll_str = open(filename).read().split('\n\n')
    tiles = [s.split(' ') for s in tile_str.split('\n')]

    # The first line contains tileset name and tile sizes
    tilefile, tilewidth, tileheight = tileset_str.split()[0:3]
    tilewidth = int(tilewidth)
    tileheight = int(tileheight)

    # Deduce the map size from tile layer
    width = len(tiles[0])
    height = len(tiles)

    # Create an in memory Gzip file to hold compressed layer data
    gzipdata = StringIO()
    rawdata = GzipFile(None, "w", 9, gzipdata)

    # Convert tile map layer into an array of 32bit integers
    for row in tiles:
        row = itertools.imap(int, row)
        rawdata.write(struct.pack("<%di" % width, *row))

    # Open the output file and generate XML
    filename = os.path.splitext(filename)[0] + ".tmx"
    outfile = open(filename, "w")

    outfile.write("""\
<?xml version="1.0" ?>
<map version="0.99b" orientation="orthogonal" \
width="%(width)d" height="%(height)d" \
tilewidth="%(tilewidth)d" tileheight="%(tileheight)d">
  <tileset firstgid="0" name="%(tilefile)s" \
tilewidth="%(tilewidth)d" tileheight="%(tileheight)d">
    <image source="%(tilefile)s"/>
  </tileset>
  <layer name="back">
    <data encoding="base64" compression="gzip">
      """ % locals())

    # Base64 encode the compressed binary data before writing to XML
    rawdata.close()
    outfile.write(base64.b64encode(gzipdata.getvalue()))
    gzipdata.close()

    outfile.write("""
    </data>
  </layer>
</map>
""")

    outfile.close()

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print "Usage: %s input.level" % sys.argv[0]
        sys.exit()

    convert(sys.argv[1])
