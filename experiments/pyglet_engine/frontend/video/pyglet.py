#!/usr/bin/env python

"""Abstraction layer to the Pyglet framework.

This module is imported internally by the frontend module when using
the Pyglet framework, and it should not be imported or accessed directly
from outside the frontend module itself.

"""

# Absolute import prevent name clash between this module and Pyglet framework
from __future__ import absolute_import

import pyglet
from pyglet.gl import *         # Quick access to gl functions and constants


class Event(object):

    @classmethod
    def run(cls):
        pass


class Image(object):
    """Proxy object for pyglet.image.AbstractImage

    The actual Pyglet image object is stored as an instance attribute
    of the Image proxy object, and the real object may be converted
    back and forth between ImageData and Texture as needed.
    
    Note that all of the factory methods will return instances of the
    derived frontend.Image object and not of this base class Image
    object.

    Instance attributes:

    _image - The underlying pyglet.image.ImageData or
        pyglet.image.Texture

    """

    @classmethod
    def load(cls, filename):
        return cls(pyglet.image.load(filename))

    @classmethod
    def create(cls, width, height):
        # TODO: Can we use Texture.create(rectangle=True) here? Does that
        # initialize the texture image like create_for_size() seems to
        return cls(pyglet.image.Texture.create_for_size(GL_TEXTURE_2D, width,
                                                        height, GL_RGBA))

    def __init__(self, pyglet_image):
        self._image = pyglet_image
        self.width = pyglet_image.width
        self.height = pyglet_image.height

    def blit(self, x, y, tint=None):
        # Caching the underlying image as a Texture may speed up future
        # rendering but I'm not totally sure.
        self._image = self._image.get_texture()
        self._image.blit(x, y)

    def blit_into(self, src, x, y):
        src._image = src._image.get_image_data()
        self._image = self._image.get_texture()
        self._image.blit_into(src._image, x, y, 0)

    def get_transform(self, flip_x=False, flip_y=False):
        pyglet_image = self._image.get_texture().get_transform(flip_x, flip_y)
        return self.__class__(pyglet_image)
        
    def get_grid(self, width, height):
        rows = self._image.height / height
        cols = self._image.width / width        
        grid = pyglet.image.ImageGrid(self._image, rows, cols, width, height)
        return [self.__class__(x) for x in grid]

    def get_region(self, x, y, width, height):
        return self.__class__(self._image.get_region(x, y, width, height))
