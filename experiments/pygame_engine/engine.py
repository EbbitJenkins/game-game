#!/usr/bin/env python

import sys      # Exit
import os       # For applying path constant
import globals  # Various
import groups   # Sprite groups
import state    # State info
import fsm      # Finite State Machine
import pygame   # Engine
import random

# Pygame 1.8.0 is missing the SDL_APPxxx bit flags!!!
pygame.APPMOUSEFOCUS = 0x01
pygame.APPINPUTFOCUS = 0x02
pygame.APPACTIVE = 0x04

# The constants used are as follows:
# winsize: initial display size for the window
# balls: the number of bouncing sprites to create
# fps: the desired frames per second
winsize = (640, 480)
balls = 100
fps = 60

# All game logic, movement speed, and object locations are based on this
# reference size of 320x240. During actual drawing, the cameara and sprite
# coordinates are scaled to match the window size. This also defines the minimum
# allowable window size the user can set.
refsize = (320, 240)

# The renderTicks variable accumulates the total number of milliseconds used to
# render each frame. The frameCount is used to display renderTicks in the windows
# title bar every second and to reset renderTicks.
renderTicks = 0
frameCount = 0

# If another application's window is selected, this becomes False and the main
# event loop pauses by blocking on pygame.event.wait() until we regain input
# focus again. Since we never get an initial ACTIVEEVENT, this variable must
# be initialized to True.
hasInputFocus = True

# Format string with stats for the window's title bar
caption = "%dx%d    Drawing: %.2fms (%2.1f%%)    Display: %2.1ffps"

# Dispatch a SDL event. Using the same function to handle events during a
# paused and an active game simplifies things.
def onEvent(event):

    # If the window is getting closed, then quit this shindig
    if event.type == pygame.QUIT:
        sys.exit()

    # If the ESC key was hit, then also quit this shindig
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        sys.exit()
    
    # If other keys are pressed or released, let player object handle it
    elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
        globals.player.do_keyboard(event.key, event.type)

    # If user resized window, then re-scale all graphics
    elif event.type == pygame.VIDEORESIZE:
        onResize(event.size)

    # If the window looses/gains input focus, update hasInputFocus
    elif event.type == pygame.ACTIVEEVENT:
        if event.state & pygame.APPINPUTFOCUS:
            global hasInputFocus
            hasInputFocus = bool(event.gain)

random.seed()
pygame.init()

# When the user resizes the main window, recreate the main display surface to
# match new window size, and reload and rescale all graphics to the new size.
def onResize(size):
    global screen, bgsize, ratio
    global tileImage, tileSize
    global ballImage, ballSize
    global bg

    # Enforce the minimum window size defined by refsize
    width = size[0] if size[0] > refsize[0] else refsize[0]
    height = size[1] if size[1] > refsize[1] else refsize[1]

    # Create 8bit color depth window display surface
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE, 8)
    bgsize = screen.get_rect()

    # Load the combined palette for all images into the screen surface.
    # All further Surface.convert() calls on other surface images will
    # remap the color indices to match the loaded palette as long as both
    # palette's have identical RGB triples somewhere. Note that we don't call
    # convert() on the palette image itself or we'd loose its color information.
    screen.set_palette(pygame.image.load("image\palette.png").get_palette())

    # The ratio between the display window size and the reference 320x240
    # resolution is used for scaling all game images and movement speeds. For
    # the most accurate scaling, the window size should be an integer multiple
    # of 320x240.
    ratio = float(bgsize.width) / refsize[0], float(bgsize.height) / refsize[1]

    # Load all image resources
    tileImage, tileRect = loadImage("tile.png")
    ballImage, ballRect = loadImage("ball.png")

    # Pre-render the background tile map
    bg = initBackground()

# Given a (x, y) tuple in the reference 320x240 coordinate space, return a new
# tuple that is scaled to match the actual window size. For the most accurate
# scaling, the window size should be an integer multiple of 320x240. This is
# function is used to scale images, coordinates, and movement speeds.
def scale((x,y)):
    return int(x * ratio[0]), int(y * ratio[1])

# Load image and return image object
def loadImage(filename):
    fullname = os.path.join(globals.imagePath, filename)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error, message:
            print 'Cannot load image:', fullname
            raise SystemExit, message
    return image, image.get_rect()

# Return random [x, y] list that can be used as a sprite/camera movement
# speed. The returned x and y values are in the range of "-speed" to "speed",
# excluding 0.
def randomSpeed(speed):
    values = range(1, speed, 1)
    values += range(-1, -speed, -1)
    return [random.choice(values), random.choice(values)]

# Return a new rectangle of the same size as (width, height) but randomly
# positioned within the reference 320x240 area such that the rect still remains
# completely visible. The new rect is suitable for use as a random starting
# location for sprites.
def randomRect((width, height)):
    x = random.randrange(refsize[0] - width)
    y = random.randrange(refsize[1] - height)
    return pygame.Rect((x, y), (width, height))

# It's more efficient to pre-render the entire scrolling tile map into an
# intermediate surface (at the appropriate size for the current window)
# and then display portions of it to the screen with a single blit(), rather
# than redrawing the background from individual tiles for each frame. Basically
# a memory vs speed tradeoff. Returns the newly created surface.
def initBackground():
    # Calculate the number of tiles that must be drawn to fully cover the
    # window. To draw partial tile images at the edges of the window, we
    # actually need one more tile in each dimension. Also since the window
    # is currently user resizable and may not be a multiple of 2, we add an
    # additional tile in each dimension just to make sure we don't wind up with
    # blank pixels somewhere.
    width, height = tileImage.get_size()
    tileColumns = bgsize.width / width + 2
    tileRows = bgsize.height / height + 2

    # Create the intermediate surface. Note that the call to convert() is
    # necessary to initialize this surface's palette to match the palette in
    # use by the screen surface.
    size = tileColumns * width, tileRows * height
    bg = pygame.Surface(size).convert()

    # Draw the tiled background to the intermediate surface
    for row in xrange(tileRows):
        for col in xrange(tileColumns):
            dest = width * col, height * row
            bg.blit(tileImage, dest)

    return bg

# Blit the global "bg" surface to the window, offsetting the upper left corner
# of "bg" by the specified pixel amount. This offset allows for a smooth
# scrolling background.
def drawBackground(offset):    
    # To draw partial tile images at the upper and left edges of the window, we
    # actually have to start drawing slightly outside of the window. Hence, the
    # subtraction of the tile width and height.
    imageSize = tileImage.get_size()
    offset = offset[0] - imageSize[0], offset[1] - imageSize[1]
    screen.blit(bg, offset)

# Update position of all the sprites and the scrolling background. Also perform
# some rudimentary edge of window collision detection on each sprite
def onUpdate(dt):
    # Leads to FSM
    fsm.curr_state = fsm.do_state(fsm.curr_state, fsm.curr_state.timer(dt))

# Draw the scrolling background and the sprites at their current locations.
# The camera and sprite locations are scaled up from their logical 320x240
# coordinates to match the actual window size.
def onDraw():
    # First blit the background so it appears underneath all sprites
    #drawBackground(scale(camera))

    # Draw player
    for sprite in groups.players:
        groups.players.draw(screen)
    

# The try..finally block ensures that pygame.quit() is always called to close the
# main window. This is necessary when running under the IDLE Python GUI since the
# Python interpreter is not actually shutdown when this piece of code finishes
# or throws an exception.
if __name__ == '__main__':
    try:
        pygame.display.set_caption("Pygame Engine")

        # The size of the real screen surface will be selectable by the user to
        # be a multiple of 320x240. We also want to set the video mode first so
        # that any subsequent surfaces we create can be convert()ed to the same
        # pixel format as the display for maximum blit speed.
        onResize(winsize)

        # Setup a random scrolling speed for the background
        scroll = randomSpeed(2)
        camera = (0, 0)

        # Create some sprites with random positions and movement speeds
        #spriteRect = [ randomRect(ballSize) for i in xrange(balls) ]
        #spriteSpeed = [ randomSpeed(5) for i in xrange(balls) ]

        # Setup a timer object to maintain consistent frame rate
        timer = pygame.time.Clock()
        
        # Setup FSM to null state
        fsm.curr_state = state.STATE_null()


        while True:
            
            # Poll for any pending events in the main loop
            for event in pygame.event.get():
                onEvent(event)            

            # If we need to pause, block on event loop until we get focus back
            while not hasInputFocus:
                onEvent(pygame.event.wait())

            # This will idle sleep to maintain the desired frame rate. I don't know
            # what I was doing wrong before, but this now this seems to be quite
            # accurate and it does away with the pygame.time.set_timer() problem
            # of flooding the event queue.
            timer.tick(fps)

            # This will be used to measure how long it takes to render a frame
            startTicks = pygame.time.get_ticks()

            # Display the previously rendered frame before drawing the current
            # one. This ensures that any variation in rendering time (due to a
            # changing number of sprites) is not visible to the user.
            pygame.display.flip()

            # Draw the current frame and update sprites/scroll for the next
            onDraw()
            onUpdate(renderTicks/100)

            # Calculate and accumulate the total elapsed time to render each frame
            renderTicks += pygame.time.get_ticks() - startTicks

            # Every second the average rendering time is calculated and displayed
            # in the window's title bar as an absolute time and a percentage out of
            # the available time per frame. If the percentage goes over 100% we
            # start dropping frames and the animation slows down.
            frameCount += 1
            if frameCount >= fps:
                average = float(renderTicks) / frameCount
                percent = (average * timer.get_fps()) / 10
                
                data = (bgsize.width, bgsize.height, average, percent, timer.get_fps())
                pygame.display.set_caption(caption % data)
                print(caption % data)

                frameCount = 0
                renderTicks = 0

    # Calling sys.exit() raises a SystemExit exception. This keeps it from propagating
    # to the IDLE Python Shell window where it would get displayed otherwise.
    except SystemExit:
        pygame.quit()
        
    finally:
        pygame.quit()