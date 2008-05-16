#!/usr/bin/env python

import sys, struct, os

def convert(filename):
    tileset_name, tile_str, coll_str = open(filename).read().split('\n\n')
    tiles = [s.split(' ') for s in tile_str.split('\n')]

    print "Map size: %dx%d" % ( len(tiles[0]), len(tiles) )

    filename = os.path.splitext(filename)[0] + ".bin"
    print "Import map to middle tile layer as 8bit 0 based:", filename
    binfile = open(filename, "wb")

    for row in tiles:
        for col in row:
            binfile.write(struct.pack("B", int(col)))

    binfile.close()

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print "Usage: %s input.level" % sys.argv[0]
        sys.exit()

    convert(sys.argv[1])
