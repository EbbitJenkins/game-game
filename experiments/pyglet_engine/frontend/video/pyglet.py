#!/usr/bin/env python

"""Abstraction layer to the Pyglet framework.

This module is imported internally by the frontend module when using
the Pyglet framework, and it should not be imported or accessed directly
from outside the frontend module itself.

"""

# Absolute import prevents name clash between this module and Pyglet framework
from __future__ import absolute_import

import pyglet
from pyglet.gl import *         # Quick access to gl functions and constants
from pyglet.window import key   # Quick access to key codes

import frontend

class App(frontend.App):

    UP = key.UP
    DOWN = key.DOWN
    LEFT = key.LEFT
    RIGHT = key.RIGHT
    JUMP = key.LSHIFT
    FIRE = key.LCTRL
    START = key.ENTER
    MENU = key.ESCAPE

    def run(self, width, height):
        window = pyglet.window.Window(width, height)

        @window.event
        def on_key_press(symbol, modifiers):
            self.on_key_press(symbol)

        @window.event
        def on_key_release(symbol, modifiers):
            self.on_key_release(symbol)

        # Turn on alpha transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        pyglet.clock.schedule(self.on_frame)
        pyglet.app.run()


class Image(frontend.Image):
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

    @staticmethod
    def load(filename):
        _image = pyglet.image.load(filename)
        return Image(_image, _image.width, _image.height)

    @staticmethod
    def create(width, height):
        # TODO: Can we use Texture.create(rectangle=True) here? Does that
        # initialize the texture image like create_for_size() seems to
        _image = pyglet.image.Texture.create_for_size(GL_TEXTURE_2D, width,
                                                      height, GL_RGBA)
        return Image(_image, width, height)

    def _blit(self, x, y, tint=None):
        # Caching the underlying image as a Texture may speed up future
        # rendering but I'm not totaly sure.
        self._image = self._image.get_texture()
        self._image.blit(x, y)

    def blit_into(self, src, x, y):
        src._image = src._image.get_image_data()
        self._image = self._image.get_texture()
        self._image.blit_into(src._image, x, y, 0)

    def get_transform(self, flip_x=False, flip_y=False):
        _image = self._image.get_texture().get_transform(flip_x, flip_y)
        return Image(_image, self.width, self.height)
        
    def get_grid(self, width, height):
        rows = int(self.height / height)
        cols = int(self.width / width)
        grid = pyglet.image.ImageGrid(self._image, rows, cols, width, height)

        # Wrap each of the created Pygame surfaces in an Image object
        return [Image(x, width, height) for x in grid]

    def get_region(self, x, y, width, height):
        _image = self._image.get_region(x, y, width, height)
        return Image(_image, width, height)

