#!/bin/usr/env python

import sys, pygame

def LoadTileset(filename):
    """
    Load a tile or sprite set into memory as individual tiles.

    The filename can be any graphics format supported by pygame.image.load()
    and the individual tile/sprites must be a multiple of 8 pixels in size
    (the width and height can be different). There must also be a single pixel
    border dividing each row and column of tiles.

    This function will autodetect the number of tiles and tile size from the
    overall image size, and it will return a list of pygame.Surfaces for each
    tile.
    """

    # Load source image into memory
    image = pygame.image.load(filename)
    (imgWidth, imgHeight) = image.get_size()

    # Guess an individual tile size (width or height) based on the total image
    # size (in the same dimension). Assumes that the tile sizes are a multiple
    # of 8 and the image contains 1 pixel dividers between each row and column
    # of tiles.
    def guess(imgSize):
        tileSize = 8
        
        while tileSize <= imgSize:
            numTiles = imgSize / tileSize
            numBorders = imgSize % tileSize

            # If tile size guess is correct, there should be the same number of
            # leftover pixels as there are dividers between individual tiles.
            # The image may or may not have an extra border on the bottom or
            # right edge, hence the two checks below            
            if numBorders == numTiles or numBorders == numTiles - 1:
                return tileSize

            tileSize = tileSize * 2

        raise "Wrong image size for 8*N tile size in %s" % filename

    # Compute the individual tile size based on the overall image size
    tileWidth = guess(imgWidth)
    tileHeight = guess(imgHeight)
    origin = pygame.Rect(0, 0, tileWidth, tileHeight)
    
    # Split the loaded image surface into individual tiles in row major order
    # from left to right and top to bottom. The integer division of the image
    # size by the tile size gives the total number of tiles in each dimension
    tileset = []
    for row in xrange(imgHeight / tileHeight):
        for col in xrange(imgWidth / tileWidth):
            box = origin.move(col * (tileWidth + 1), row * (tileHeight + 1))
            tileset.append( image.subsurface(box) )

    return tileset

def SaveTileset(filename, tileset):
    """
    Save a tile or sprite set as a single image file.

    The tileset must be a list of pygame.Surfaces, all of which must have the
    same size that is a multiple of 8 pixels (the width and height can be
    different). The individual tiles are layed out along a single row in the
    image with no intervening spaces between. The filename can have any
    extension supported by pygame.image.save().

    Note: Saving in .png format appears broken and produces corrupt files.
    """

    # Create a new destination image large enough to hold all the tiles
    (tileWidth, tileHeight) = tileset[0].get_size()
    image = pygame.Surface( (tileWidth * len(tileset), tileHeight) )

    # Blit the tiles to destination image along one row
    origin = pygame.Rect(0, 0, tileWidth, tileHeight)
    for i in xrange(len(tileset)):
        image.blit(tileset[i], origin.move(i * tileWidth, 0))

    # Save the destination image to disk
    pygame.image.save(image, filename)

if __name__ == "__main__":
    pygame.init()

    if len(sys.argv) != 3:
        print "Usage: %s input.png output.png" % sys.argv[0]
        sys.exit()

    tileset = LoadTileset(sys.argv[1])
    SaveTileset(sys.argv[2], tileset)
