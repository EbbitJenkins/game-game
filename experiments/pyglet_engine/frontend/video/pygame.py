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
    def create(cls, width, height):
        pass

    def __init__(self, pygame_surface):
        self._surface = pygame_surface

    def blit(self, x, y, tint=None):
        pass

    def blit_into(self, src, x, y):
        pass

    def get_transform(self, flip_x=False, flip_y=False):
        pass
        
    def get_grid(self, width, height):
        pass

    def get_region(self, x, y, width, height):
        pass
