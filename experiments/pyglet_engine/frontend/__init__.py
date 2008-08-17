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
These options are also removed from sys.argv, allowing the main line
code to report an error if any remaining (unknown) options are found
on the command line.

"""

# The real abstraction is provided by the video.pyglet and
# video.pygame modules which subclass the Image and App base classes
# in this module. These frontend base classes are mostly there to
# provide some common functionality and a documented public interface
# for the main game engine.

# TODO: I could create a dummy _video proxy object that will throw an
# exception if the init() function has not been called yet and the
# real _video module is not yet loaded.

# TODO: The frontend will need to load a window icon, load the 256 color
# palette image for Pygame, and set a window caption. We can pass all this
# in through the init() method.

# TODO: The frontend will have to read/write a ConfigParser in the
# user's home directory to load/save any graphics options or input
# mappings the user has changed. Unfortunately the scan codes differ
# between Pygame and Pyglet so we'll need two setup files and if the
# user switches frameworks they'll have to redefine their inputs.

# TODO: On Windows we'll eventually run with pythonw.exe (i.e. no console)
# if we can't initialize either Pygame or Pyglet we need to call
# User32.MessageBox() to print the error. Either we need Python 2.5 for
# ctypes or we need to include the pywin32 extensions in the Windows
# installer.

# TODO: We need a separate Image for loading from a file and a Surface
# for blitting into. The main interface difference is that Image is
# read only while a Surface has blit_into(). Also, Images are
# automatically rescaled by the frontend, while a Surface has to be
# recreated by the game engine on every resize through the on_reload()
# event. UPDATE: With my current way of thinking, a separate Image and
# Surface will not be necessary. I'll know for sure once I actually
# have scaling, and then I can remove this comment for good.


class ExampleEventHandler:
    """Example high-level event handler class.

    This class provides examples of all possible events that can be
    sent to an event handler registered with Event.push(). Any object
    can act as an event handler if it contains one or more methods
    with the same names as shown in this class.

    TODO: We can re-arrange all of these events if necessary. For
    example, we can have a single on_key_press/on_key_release that
    takes some generic scan code if that makes more sense for the main
    game engine. My assumption has been that each of these actions
    will require somewhat different code so might as well use a
    separate function for every event.

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

    def on_menu_left(self):
        pass
    
    def on_menu_right(self):
        pass
    
    def on_menu_up(self):
        pass
    
    def on_menu_down(self):
        pass


class InitError(RuntimeError):
    pass


class App(object):
    """Low-level event loop abstration.

    The singleton App class provides an abstraction over the low-level
    events specific to the Pyglet or Pygame frameworks by dispatching
    high-level events to handlers registered with push(). The class
    also provides methods to (re)map low-level events like keys or
    gamepad buttons to high-level events like "jump" and "fire".

    Use the app() function to return the singleton instance of this
    class.

    TODO: Need to add fps, vsync, etc. attributes that video.pyglet
    will use to schedule timers, etc.

    """

    # Stack of event handlers; active handler at the end of the list.
    # There is always a dummy entry on the bottom of the stack, so the
    # dispatch() method doesn't have to check for an empty stack.
    _stack = [None]
        
    def on_key_press(self, key):
        if key in _key_press_table:
            self.dispatch(_key_press_table[key])

    def on_key_release(self, key):
        if key in _key_release_table:
            self.dispatch(_key_release_table[key])
        
    def on_frame(self, dt):
        # TODO: Add the logic here to generate virtual logic frames
        # based on the elapsed dt time.
        self.dispatch("on_update")
        self.dispatch("on_draw")
    
    def dispatch(self, event):
        handler = self._stack[-1]
        if hasattr(handler, event):
            getattr(handler, event)()

    def push(self, handler):
        """Push an event handler on top of the event handler stack.

        The event handler becomes the new active one receiving all
        future events.

        """
        self._stack.append(handler)

    def pop(self):
        """Pop the top most handler off of the event handler stack.

        If the stack is already empty, this function does nothing.

        """
        if len(self._stack) > 1:
            self._stack.pop()

    def run(self, width, height):
        """Enter the main event loop.

        Calling this method starts the frame timer and begins
        dispatching events to the event handler on top of the stack.
        This method never returns altough it raises SystemExit when
        quiting the game.

        The width/height arguments give the initial size of the main
        game window. In the real game though, the main window is
        always 320x240 (even if resized) so this won't be necessary.

        """

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
class Image(object):
    """A single image that can be drawn to screen or drawn into.

    New Image objects are created by calling the image.load() or
    image.create() factory methods, and by calling the get_xxx()
    methods of an existing Image to obtain a modified version of the
    original. However, an Image object should not be instantiated
    directly by outside code.

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

    @staticmethod
    def load(filename):
        """Create and return an Image object loaded from a file."""
        return _video.Image.load(filename)

    @staticmethod
    def create(width, height):
        """Create and return a new Image object of the given size.

        Note that the Image canvas may initially contain garbage data.
        It is the caller's responsibility to completely fill the
        entire image surface with one or more blit_into() calls.

        """
        return _video.Image.create(width, height)

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

        # TODO: Provide an area and prev_area tuple argument that
        # blits only a subregion of the image. This allows interpolation
        # of the camera position and under Pygame is also more efficient
        # because a separate subsurface doesn't have to be created
        # on every display frame; Surface.blit() already takes an area
        # argument.

        # TODO: Add common code to do the interpolation and pass the
        # computed x,y to the derived class _blit()
        self._blit(x, y, tint)

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

    def get_transform(self, flip_x=False, flip_y=False):
        """Return a new horizontally and/or vertically flipped Image.

        The original image is not modified. The same concerns about
        sharing of the pixel buffers between the original and new
        Image apply as in the get_grid() method.

        """

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

    def get_region(self, x, y, width, height):
        """Return an Image created from a rectangular region of the
        original image.

        The original Image is not modified. The same concerns about
        sharing of the pixel buffers between the original and new
        Image apply as in the get_grid() method.

        """


# TODO: Eventually this will be a conditional import to select Pygame
# or Pyglet based on command line options. It will also check for
# ImportErrors to automatically try the other framework if the one
# requested is not available.
def init(options):
    """Initialize the frontend module

    This function should be called once to initialize the frontend
    module and import either the Pygame or Pyglet framework.

    The options argument is the same as the options object returned by
    Optionparser.parse_args(). It chooses which framework to use and
    how to initialize it.

    """
    
    global _app
    global _video
    global _key_press_table
    global _key_release_table

    # Do nothing if module is already initialized
    if _app:
        return
    
    # If a specific framework was requested, then use only it. Let the
    # exception fall through if the given framework cannot initialize
    if options.video == "pygame":
        from frontend.video import pygame as _video
    elif options.video == "pyglet":
        from frontend.video import pyglet as _video

    # If no specific framework was given, default to Pygame software
    # rendering (for max compatibility), but fall back to Pyglet if
    # Pygame/SDL cannot import or initialize. If neither framework
    # modules can be imported or initialize, then raise an exception
    # encapsulating the individual exceptions returned by both
    # frameworks.
    else:
        try:
            from frontend.video import pygame as _video
        except (ImportError, InitError), e1:
            try:
                from frontend.video import pyglet as _video
            except (ImportError, InitError), e2:
                # TODO: What we could really use at this point are
                # chained exceptions. But since those will not be around
                # until Python 3000 (PEP 344), I'll have to hack something
                # up myself with FrontendInitError
                raise

    # Create the singleton App object to initialize frontend module
    _app = _video.App()

    # The press/release event dispatch tables can now be initialized
    # because the framework specific low-level events are now
    # available.
    _key_press_table = { _app.UP: "on_up_press",                         
                         _app.DOWN: "on_down_press",
                         _app.LEFT: "on_left_press",
                         _app.RIGHT: "on_right_press",
                         _app.FIRE: "on_fire",
                         _app.JUMP: "on_jump",
                         _app.START: "on_start",
                         _app.MENU: "on_menu" }

    _key_release_table = { _app.UP: "on_up_release",
                           _app.DOWN: "on_down_release",
                           _app.LEFT: "on_left_release",
                           _app.RIGHT: "on_right_release" }


def app():
    """Return the singleton App object"""
    return _app

# Event dispatch table mapping key scan codes for low-level key
# press/release events to the name of a high level event handler.
# Initialized by the init() method once a specific framework is loaded
# and the App object has been created
_key_press_table = None
_key_release_table = None

# The singleton instance of the App() class created by the
# _video.init() function.
_app = None
