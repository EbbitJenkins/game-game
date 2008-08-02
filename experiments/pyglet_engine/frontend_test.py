#!/usr/bin/env python

from pyglet import image

import frontend


# This is an informal unit test of sorts

blank = frontend.Image.create(100, 100)
assert(isinstance(blank, frontend.Image))
assert(isinstance(blank._image, image.Texture))
assert(blank.width >= 100 and blank.height >= 100)

pict = frontend.Image.load("bullet.png")
assert(isinstance(pict, frontend.Image))
assert(isinstance(pict._image, image.ImageData))
assert(pict.width == 8 and pict.height == 8)

blank_region = blank.get_region(10, 20, 4, 4)
assert(isinstance(blank_region, frontend.Image))
assert(isinstance(blank_region._image, image.TextureRegion))
assert(blank_region.width == 4 and blank_region.height == 4)

pict_region = pict.get_region(2, 3, 4, 4)
assert(isinstance(pict_region, frontend.Image))
assert(isinstance(pict_region._image, image.ImageDataRegion))
assert(pict_region.width == 4 and pict_region.height == 4)

pict_region.blit_into(blank_region, 0, 0)
assert(isinstance(pict_region._image, image.Texture))
assert(isinstance(blank_region._image, image.ImageData))

blank_region.blit_into(pict_region, 0, 0)
assert(isinstance(pict_region._image, image.ImageData))
assert(isinstance(blank_region._image, image.Texture))

grid = pict.get_grid(3, 3)
assert(len(grid) == 4)
assert(all([isinstance(x, frontend.Image) for x in grid]))
assert(all([isinstance(x._image, image.ImageDataRegion) for x in grid]))

grid = blank.get_grid(blank.width / 10, blank.height / 10)
assert(len(grid) == 100)
assert(all([isinstance(x, frontend.Image) for x in grid]))
assert(all([isinstance(x._image, image.TextureRegion) for x in grid]))

blank.blit(0, 0)
assert(isinstance(blank._image, image.Texture))

pict.blit(0, 0)
assert(isinstance(pict._image, image.Texture))

#print all([isinstance(x, image.
