#!/usr/bin/env python

"""Abstraction layer to the Pygame framework.

This module is imported internally by the frontend module when using
the Pygame framework, and it should not be imported or accessed directly
from outside the frontend module itself.

"""

# Absolute import prevents name clash between this module and Pygame framework
from __future__ import absolute_import
import sys

import pygame

import frontend

# TODO: We can use a weakref dictionary to track all the Image objects
# still in use. That way we know what images to re-create when
# pre-scaling images for a new window size or when DirectDraw
# HWSURFACEs are lost after the game in minimized and restored.


class App(frontend.App):

    UP = pygame.K_UP
    DOWN = pygame.K_DOWN
    LEFT = pygame.K_LEFT
    RIGHT = pygame.K_RIGHT
    JUMP = pygame.K_LSHIFT
    FIRE = pygame.K_LCTRL
    START = pygame.K_RETURN
    MENU = pygame.K_ESCAPE

    def run(self, width, height):
        global _display

        # Create display surface of the requested size
        # TODO: This should be an 8 bit surface
        _display = pygame.display.set_mode((width, height))

        # The try..finally block ensures that pygame.quit() is always
        # called to close the main window. This is necessary when
        # running under the IDLE Python GUI since the Python
        # interpreter is not actually shutdown when this piece of code
        # finishes or throws an exception.
        try:
            # Setup a timer object to maintain consistent frame rate
            timer = pygame.time.Clock()

            # Used to keep track of elapsed time between each frame
            prev_frame_ticks = pygame.time.get_ticks()

            while True:

                # Poll for any pending events in the main loop
                for event in pygame.event.get():

                    if event.type == pygame.QUIT:
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        self.on_key_press(event.key)
                    elif event.type == pygame.KEYUP:
                        self.on_key_release(event.key)
                    #elif event.type == pygame.VIDEORESIZE:
                    #elif event.type == pygame.ACTIVEEVENT:
                    #    if event.state & pygame.APPINPUTFOCUS:


                # This will idle sleep to maintain the desired frame
                # rate. Note that since there is no vsync on
                # SWSURFACEs, if the frame rate is too close to the
                # monitor's refresh rate (or an integer multiple of
                # the refresh), it will result in jerky animation.
                #
                # TODO: Need to have a property in the frontend that
                # we can use here.
                timer.tick(75)

                # Display the previously rendered frame before drawing
                # the current one. This ensures that any variation in
                # rendering time (due to a changing number of sprites)
                # is not visible to the user.
                pygame.display.flip()

                # The measured elapsed time between each physical frame
                # is used to maintain a constant virtual frame rate
                cur_frame_ticks = pygame.time.get_ticks()                
                self.on_frame(cur_frame_ticks - prev_frame_ticks)
                prev_frame_ticks = cur_frame_ticks

        finally:    
            pygame.quit()

class Image(frontend.Image):
    """Proxy object for pygame.Surface

    The actual Pygame Surfaces used by this Image are stored as instance
    attributes of this proxy object.
    
    Instance attributes:

    width,height - The size of the Image in pixels.

    _image - Underlying SWSURFACE pygame.Surface at original resolution

    _scaled - TODO: A scaled (and possibly a HWSURFACE) pygame.Surface
        ready for blitting to screen. The on_reload() event recreates
        this surface from _image to match the current window size.

    """
    # TODO: What are the implications of Surface.subsurface() on a
    # HWSURFACE? If we can't allow it then we'll just duplicate the
    # original surface.

    @staticmethod
    def load(filename):
        # TODO: If we're going to use 24bit images, then convert this
        # image into 8 bit right here so that further scaling/flipping
        # operations will run faster.
        _image = pygame.image.load(filename)
        width, height = _image.get_size()
        return Image(_image, width, height)

    @staticmethod
    def create(width, height):
        _image = pygame.Surface((width, height))
        return Image(_image, width, height)

    def _blit(self, x, y, tint=None):
        # TODO: We should maintain our own windows size variable instead of
        # having to get it from the Pygame Surface each time.
        window_height = _display.get_size()[1]
        _display.blit(self._image, (x, window_height - y - self.height))

    def blit_into(self, src, x, y):
        self._image.blit(src._image, (x, self.height - y - src.height))

    def get_transform(self, flip_x=False, flip_y=False):
        _image = pygame.transform.flip(self._image, flip_x, flip_y)
        return Image(_image, self.width, self.height)
        
    def get_grid(self, width, height):
        # To maintain the Pyglet coordinate convention, the
        # subsurfaces must be created in bottom-up and left-right
        # order along the original image.
        grid = []
        for y in xrange(0, self.height, height):
            for x in xrange(0, self.width, width):
                y = self.height - y - height
                grid.append(self._image.subsurface(x, y, width, height))

        # Wrap each of the created Pygame surfaces in an Image object
        return [Image(x, width, height) for x in grid]

    def get_region(self, x, y, width, height):
        y = self.height - y - height
        _image = self._image.subsurface((x, y, width, height))
        return Image(_image, width, height)

    def on_reload():
        # TODO: Take care of resizing surfaces here by going through the
        # weakref dictionary of all Images that are still active
        pass


pygame.init()
#pygame.display.init()

# The window display pygame.Surface. Initialized by the Event.run() method
_display = None
