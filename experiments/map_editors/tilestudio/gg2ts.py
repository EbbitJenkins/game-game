#!/usr/bin/env python

import sys, struct, os, itertools

def convert(filename):
    tileset_name, tile_str, coll_str = open(filename).read().split('\n\n')
    tiles = [s.split(' ') for s in tile_str.split('\n')]

    width = len(tiles[0])
    print "Map size: %dx%d" % (width, len(tiles))

    filename = os.path.splitext(filename)[0] + ".bin"
    print "Import map to middle tile layer as 8bit 0 based:", filename
    binfile = open(filename, "wb")

    for row in tiles:        
        # Tile number 0 in ASCII map represents an absent tile which is -1 in
        # Tile Studio. Also, the tile numbers in the ASCII map are 1 based
        # while Tile Studio is 0 based, so all the tile numbers are simply
        # shifted over by one.
        row = itertools.imap(lambda x: int(x) - 1, row)
        binfile.write(struct.pack("%db" % width, *row))

    binfile.close()

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print "Usage: %s input.level" % sys.argv[0]
        sys.exit()

    convert(sys.argv[1])
