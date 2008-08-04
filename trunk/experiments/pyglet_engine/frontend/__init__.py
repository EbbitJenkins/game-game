#!/usr/bin/env python

"""Low-level services and abstraction layer to Pygame/Pyglet.

The services provided by the front end include frame timing with fixed
virtual logic rate, image blitting with linear interpolation of
position, low-level event handling with user-defined input remapping,
start-up and command line parsing, window resizing while maintaining
aspect ratio, and abstraction to the Pygame and Pyglet frameworks
including coordinate system conversion.

Note that the blit routines in this module assume a base 320x240
resolution and use the Pyglet/OpenGL coordinate convention (the origin
is in the lower-left corner and the Y axis increases in the up
direction).

When this module is imported for the first time, it will automatically
parse any command line arguments used to select the video/audio modes
and use them to initialize the appropriate Pygame or Pyglet framework.

"""

# The real abstraction is provided by the video.pyglet and
# video.pygame modules which provide the Image and EventHandler base
# classes used by this module. The frontend subclasses are mostly just
# wrappers around the base classes providing some common functionality
# and a documented public interface for the main game engine.

# TODO: Eventually this will be a conditional import to select Pygame
# or Pyglet based on command line options. It will also check for
# ImportErrors to automatically try the other framework if the one
# requested is not available.
from frontend.video import pyglet as _video

# TODO: The frontend will need to load a window icon, load the 256 color
# palette image for Pygame, and set a window caption. Not sure what the
# best way is to specify that. We can hardcode it into the frontend, have
# the frontend get it directly via the manifest module from an "init"
# Manifest, or perhaps pass it as arguments into the EventHandler.run()
# method.

# TODO: The frontend will have to read/write a ConfigParser in the
# user's home directory to load/save any graphics options or input
# mappings the user has changed. Unfortunately the scan codes differ
# between Pygame and Pyglet so we'll need two setup files and if the
# user switches frameworks they'll have to redefine their inputs.

# by the platform OS, I'm hoping that Pygame and Pyglet both report
# the same numbers. That would allow one config file per platform to
# work with either framework.

# TODO: On Windows we'll eventually run with pythonw.exe (i.e. no console)
# if we can't initialize either Pygame or Pyglet we need to call
# User32.MessageBox() to print the error. Either we need Python 2.5 for
# ctypes or we need to include the pywin32 extensions in the Windows
# installer.


class ExampleEventHandler:
    """Example high-level event handler class.

    This class provides examples of all possible events that can be
    sent to an event handler registered with Event.push(). Any object
    can act as an event handler if it contains one or more methods
    with the same names as shown in this class.

    TODO: We can re-arrange all of these events if necessary. For
    example, we can have a single on_key_press/on_key_release that
    takes some generic scan code if that makes more sense for the main
    game engine. My assumption has been that since each of these
    actions will require possibly very different code so might as well
    separate every event into a separate function.

    """

    def on_draw(self):
        pass

    def on_update(self):
        pass
    
    def on_fire(self):
        pass

    def on_jump(self):
        pass

    def on_start(self):
        pass

    def on_menu(self):
        pass

    def on_left_press(self):
        pass

    def on_left_release(self):
        pass

    def on_right_press(self):
        pass

    def on_right_release(self):
        pass

    def on_up_press(self):
        pass

    def on_up_release(self):
        pass

    def on_down_press(self):
        pass

    def on_down_release(self):
        pass


class Event(_video.Event):
    """Low-level event loop abstration.

    The Event class provides an abstraction over the low-level events
    specific to the Pyglet or Pygame frameworks by dispatching
    high-level events to handlers registered with push(). The class
    also provides methods to (re)map low-level events like keys or
    gamepad buttons to high-level events like "jump" and "fire".

    TODO: Need to add fps, vsync, etc. attributes that video.pyglet
    will use to schedule timers, etc.

    """

    # Stack of event handlers; active handler at the end of the list.
    # There is always a dummy entry on the bottom of the stack, so the
    # dispatch() method doesn't have to check for an empty stack.
    _stack = [None]
        
    @classmethod
    def on_key_press(cls, key):
        if key in _key_press_table:
            cls.dispatch(_key_press_table[key])

    @classmethod
    def on_key_release(cls, key):
        if key in _key_release_table:
            cls.dispatch(_key_release_table[key])
        
    @classmethod
    def on_frame(cls, dt):
        # TODO: Add the logic here to generate virtual logic frames
        # based on the elapsed dt time.
        cls.dispatch("on_update")
        cls.dispatch("on_draw")
        
    @classmethod
    def dispatch(cls, event):
        handler = cls._stack[-1]
        if hasattr(handler, event):
            getattr(handler, event)()

    @classmethod
    def push(cls, handler):
        """Push an event handler on top of the event handler stack.

        The event handler becomes the new active one receiving all
        future events.

        """
        cls._stack.append(handler)

    @classmethod
    def pop(cls):
        """Pop the top most handler off of the event handler stack.

        If the stack is already empty, this function does nothing.

        """
        if len(cls._stack) > 1:
            cls._stack.pop()

    # It may be more appropriate to make this a global function of the
    # module since we may want to delay the creation of the main
    # window until run() is called.
    @classmethod
    def run(cls, width, height):
        """Enter the main event loop.

        Calling this method starts the frame timer and begins
        dispatching events to the event handler on top of the stack.
        This method never returns altough it raises SystemExit when
        quiting the game.

        The width/height arguments give the initial size of the main
        game window. In the real game though, the main window is
        always 320x240 (even if resized) so this won't be necessary.

        """
        super(Event, cls).run(width, height)

# TODO: May need to have clear() method that erases a rectangular area
# of an image (or the entire image) and makes it transparent again.
# This would be usefull for debug output like an ever changing frame
# rate (printed by a FontRenderer) overlaid on top of the running
# game. Under Pygame we can use draw.rect() or surface.fill() with the
# transparent color key. Under Pyglet the only method I could find is
# to use a SolidColorImagePattern() to create ImageData with alpha=0
# and then blit that into a Texture; maybe there's a low-level OpenGL
# call I can use to do the same thing more efficiently?
#
# TODO: Add an open() and close() method to Image to control when the
# image can be drawn to screen or drawn into. In Pygame this will
# control RLEACCEL on the color key. Eventually it can also be used to
# build up an OpenGL display list for blit_into() operations.
# Using an OpenGL display list would also solve the problem of a clear()
# method: just delete the display list and you've got a transparent "image"
# again.
class Image(_video.Image):
    """A single image that can be drawn to screen or drawn into.

    New Image objects are created by calling the load() or new() class
    methods, or by calling the get_xxx() methods of an existing Image
    to obtain a modified version of the original. However, an Image
    object should not be instantiated directly by outside code.

    An Image object may be blitted to the screen, and other Image
    objects may be blitted into an Image object.

    The Image object acts as a proxy for the real Pygame Surface or
    Pyglet Texture/ImageData/. Using a proxy allows the frontend
    to re-create the underlying images as needed, without the main
    game engine being aware since the proxy Image object is left
    intact. For example, each time the window size changes, the Pygame
    abstraction layer has to re-create and re-scale all of the
    underlying Pygame Surfaces.

    Instance attributes:

    width,height - The size of the Image in pixels.

    """

    @classmethod
    def load(cls, filename):
        """Create and return an Image object loaded from an file."""
        image_and_size = super(Image, cls).load(filename)
        return cls(*image_and_size)

    @classmethod
    def create(cls, width, height):
        """Create and return a new Image object of the given size.

        Note that the Image canvas may initially contain garbage data.
        It is the caller's responsibility to completely fill the
        entire image surface with one or more blit_into() calls.

        """
        _image = super(Image, cls).create(width, height)
        return cls(_image, width, height)

    def __init__(self, _image, width, height):
        self._image = _image
        self.width = width
        self.height = height

    def blit(self, x, y, prev_x=None, prev_y=None, tint=None):
        """Draw Image to the screen at an interpolated position.

        Drar this Image at an interpolated position between point (x,
        y) and (prev_x, prev_y). The (x, y) coordinate should be the
        Image's position from the last virtual frame (i.e. on_update()
        event), and the (prev_x, prev_y) should be the position from
        the second to last virtual frame. The interpolation factor is
        based on the elapsed time since the last virtual frame.

        If coordinate (prev_x, prev_y) is omitted or is the same as
        (x, y), then no interpolation will be performed. When an Image
        is first displayed on screen or when an Image "jumps" from one
        position to another, no interpolation should take place.

        The tint argument is a (R, G, B) tuple applied as a color tint
        to every opaque pixel. Color tints can indicate different
        kinds of damage that a mobile can take. For example, a yellow
        tint could indicate regular damage, a green tint can show
        radiation or poison damage, while a red tint could be used for
        fire damage.

        """

        # TODO: Add common code to do the interpolation and pass the
        # computed x,y to the base class blit()
        super(Image, self).blit(x, y, tint)

    def blit_into(self, src, x, y):
        """Blit another Image into this one.

        Blit the Image src into this image at position (x, y).
        
        Keep in mind that blitting to an Image may be slower than than
        blitting to the screen. For exmaple, when using Pyglet over
        remote X11 with the GLX extension, every blit of an image to
        another sends the raw bitmap over the network. If the
        underlying Pyglet object for the source is a Texture, it would
        actually take two bitmap transfers.

        """
        super(Image, self).blit_into(src, x, y)

    def get_transform(self, flip_x=False, flip_y=False):
        """Return a new horizontally and/or vertically flipped Image.

        The original image is not modified. The same concerns about
        sharing of the pixel buffers between the original and new
        Image apply as in the get_grid() method.

        """
        _image = super(Image, self).get_transform(flip_x, flip_y)
        return self.__class__(_image, self.width, self.height)

    def get_grid(self, width, height):
        """Return a list of new Images by subdividing the original
        image into a grid.

        This method is intended for separating the individual frames
        on a sprite sheet. The width and height give the size of a
        single frame, and the image is subdivided in rows from the
        bottom left corner to the upper right (Pyglet convention). The
        number of Images in the returned list depends on the total
        size of the original Image.

        The returned Images may or may not share their pixel buffers
        with the original Image. Callers should not depend on either
        behavior and therefore should avoid modifying the returned
        Images. If the original Image is modified, this method should
        be called again to return a new sequence of sub images.

        """
        grid = super(Image, self).get_grid(width, height)
        return [self.__class__(x, width, height) for x in grid]

    def get_region(self, x, y, width, height):
        """Return an Image created from a rectangular region of the
        original image.

        The original Image is not modified. The same concerns about
        sharing of the pixel buffers between the original and new
        Image apply as in the get_grid() method.

        """
        _image = super(Image, self).get_region(x, y, width, height)
        return self.__class__(_image, width, height)


# Event dispatch table mapping key scan codes for a low-level key
# press event to the name of a high level event handler.
_key_press_table = { Event.UP: "on_up_press",                         
                     Event.DOWN: "on_down_press",
                     Event.LEFT: "on_left_press",
                     Event.RIGHT: "on_right_press",
                     Event.FIRE: "on_fire",
                     Event.JUMP: "on_jump",
                     Event.START: "on_start",
                     Event.MENU: "on_menu" }

# Dispatch table for key release events
_key_release_table = { Event.UP: "on_up_release",
                       Event.DOWN: "on_down_release",
                       Event.LEFT: "on_left_release",
                       Event.RIGHT: "on_right_release" }
