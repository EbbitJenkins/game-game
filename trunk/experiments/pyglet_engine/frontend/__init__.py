#!/usr/bin/env python

"""Low-level services and abstraction layer to Pygame/Pyglet

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
and uses them to initialize the appropriate Pygame or Pyglet
framework.

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
import frontend.video.pyglet as _video

__all__  = ["EventHandler", "Image"]


class EventHandler(_video.EventHandler):
    """High-level event handler.

    This base class provides dummy event handler methods for all
    high-level events delivered by the frontend. Actual event handlers
    should extend this class

    The Event class provides a high-level event abstraction over the
    low-level events specific to the Pyglet or Pygame frameworks. The
    class provides methods to register high-level event handlers and
    to (re)map low-level events like keys or gamepad buttons to
    high-level events like "jump" and "fire".

    """

    def push(self):
        """Push this event handler on top of the event handler stack.

        This event handler becomes the new active one receiving all
        future events. The supplied handler should be a subclass of
        the EventHandler class.

        """

    @classmethod
    def pop(cls):
        """Pop the top most handler off of the event handler stack."""

    @classmethod
    def top(cls):
        """Return the active event handler on top of the stack."""

    @classmethod
    def run(cls):
        """Enter the main event loop.

        Calling this method starts the frame timer and begins
        dispatching events to the event handler on top of the stack.
        This method never returns altough it raises SystemExit when
        quiting the game.

        """
        super(EventHandler, cls).run()

# TODO: Add an open() and close() method to Image to control when the
# image can be drawn to screen or drawn into. In Pygame this will
# control RLEACCEL on the color key. Eventually it can also be used to
# build up an OpenGL display list for blit_into() operations.
class Image(_video.Image):
    """A single image that can be drawn to screen or drawn into.

    New Image objects are created by calling the load() or new() class
    methods, or by calling the get_xxx() methods of an existing Image
    to obtain a modified version of the original. However, an Image
    object should not be instantiated directly by outside code.

    An Image object may be blitted to the screen, and other Image
    objects may be blitted into an Image object.

    The Image object acts as a proxy for the real Pygame Surface or
    Pyglet Texture/ImageData/Sprite. Using a proxy allows the frontend
    to re-create the underlying images as needed, without the main
    game engine being aware since the proxy Image object is left
    intact. For example, each time the window size changes, the Pygame
    abstraction layer has to re-create and re-scale all of the
    underlying Pygame Surfaces.

    """

    @classmethod
    def load(cls, filename):
        """Create and return a new Image object from an image file."""
        return super(Image, cls).load(filename)

    @classmethod
    def new(cls, width, height):
        """Create and return a new Image object of the given size.

        Note that the Image canvas may initially contain garbage data.
        It is the caller's responsibility to completely fill the
        entire image surface with one or more blit_into() calls.

        """
        return super(Image, cls).new(width, height)

    def blit(self, x, y, prev_x=None, prev_y=None):
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

        """
        super(Image, self).blit(x, y, prev_x, prev_y)

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

    def get_tint(self, color):
        """Return a new Image with a color tint.

        The color argument is a (R, G, B) tuple applied as a color
        tint to every opaque pixel. The original Image is not
        modified.

        Color tints can indicate different kinds of damage that a
        mobile can take. For example, a yellow tint could indicate
        regular damage, a green tint can show radiation or poison
        damage, while a red tint could be used for fire damage.

        """
        return super(Image, self).new_tint(color)

    def get_transform(self, flip_x=False, flip_y=False):
        """Return a new horizontally and/or vertically flipped Image.
        The original image is not modified.

        """
        return super(Image, self).new_transform(flip_x, flip_y)

    def get_grid(self, width, height):
        """Return a sequence of Images by subdividing the original
        image into a grid.

        This method is intended for separating the individual frames
        on a sprite sheet. The width and height give the size of a
        single frame, and the image is subdivided in rows from the
        bottom left corner to the upper right (Pyglet convention). The
        number of Images in the returned sequence depends on the total
        size of the original Image.

        The returned Images may or may not share their pixel buffers
        with the original Image. Callers should not depend on either
        behavior and therefore should avoid modifying the returned
        Images. If the original Image is modified, this method should
        be called again to return a new sequence of sub images.
        
        """
        return super(Image, self).new_grid(width, height)
