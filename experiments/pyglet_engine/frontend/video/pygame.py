#!/usr/bin/env python

"""Abstraction layer to the Pygame framework.

This module is imported internally by the frontend module when using
the Pygame framework, and it should not be imported or accessed directly
from outside the frontend module itself.

"""

# TODO: We can use a weakref dictionary to track all the Image objects
# still in use. That way we know what images to re-create when
# pre-scaling images for a new window size or when DirectDraw
# HWSURFACEs are lost after the game in minimized and restored.


class EventHandler(object):

    @classmethod
    def run(cls):
        pass


class Image(object):

    @classmethod
    def load(cls, filename):
        pass

    @classmethod
    def new(cls, width, height):
        pass

    def blit(self, x, y, prev_x=None, prev_y=None):
        pass

    def blit_into(self, src, x, y):
        pass

    def get_tint(self, color):
        pass

    def get_transform(self, flip_x=False, flip_y=False):
        pass
        
    def get_grid(self, width, height):
        pass
