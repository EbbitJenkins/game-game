#!/usr/bin/env python

import sys, pygame, random

# TODO: Separate the game logic from rendering better. The game logic should
# only deal with 320x240 coordinates and speeds. Right before actual blitting
# the rendering code should multiply all the coordinates by the display ratios.

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

# The ratio between the display window size and the reference 320x240 resolution
# is used for scaling all game images and movement speeds. For the most accurate
# scaling, the window size should be an integer multiple of 320x240
widthRatio = winsize[0] / 320.0
heightRatio = winsize[1] / 240.0

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
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        sys.exit()

    # If the window looses/gains input focus, update hasInputFocus
    elif event.type == pygame.ACTIVEEVENT:
        if event.state & pygame.APPINPUTFOCUS:
            global hasInputFocus
            hasInputFocus = bool(event.gain)

random.seed()
pygame.init()

# Load a sprite/game image and pre-scale it to match the output display surface.
# It turns out that the Surface.blit() routines are so optimized it's more
# efficient to pre-scale and blit at the full resolution, even when blitting
# overlapping areas, then it would be to blit at 320x240 to an intermediate
# surface and then scale the entire display in realtime. This routine also
# reindexes the images palette indices with Surface.convert().
def loadImage(filename):
    image = pygame.image.load(filename).convert()
    width, height = image.get_size()
    newwidth, newheight = int(width * widthRatio), int(height * heightRatio)
    
    return pygame.transform.scale(image, (newwidth, newheight))

# Return random [x, y] list that can be used as a sprite/camera movement
# speed. The returned x and y values are in the range of "-speed" to "speed",
# excluding 0.
def randomSpeed(speed):
    values = range(1, speed, 1)
    values += range(-1, -speed, -1)
    return [random.choice(values), random.choice(values)]

# Return a new rectangle of the same size as "rect" but randomly positioned
# within the screen area such that it still remains completely visible. The new
# rect is suitable for use as a random starting location for sprites.
def randomRect(rect):
    x = random.randrange(size.width - rect.width)
    y = random.randrange(size.height - rect.height)
    return rect.move(x, y)

# Blit a simple tiled background on the screen surface to better simulate the
# rendering load of a real game engine. The offset tuple shifts the entire
# background by that many pixels to create a scrolling effect.
def drawBackground(offset):
    # Calculate the number of tiles that must be drawn to fully cover the
    # background. If offset is not (0,0) we actually need one more tile since
    # the opposite edges of the window are each displaying partial tile images.
    tileColumns = size.width / tile.get_rect().width + 1
    tileRows = size.height / tile.get_rect().height + 1

    # To draw partial tile images at the upper and left edges of the window, we
    # actually have to start drawing slightly outside of the window. Hence, the
    # subtraction of the tile width and height.
    width, height = tile.get_rect().width, tile.get_rect().height
    offset = (offset[0] - width, offset[0] - height)

    # Draw the tiled background shifted over by "offset" pixels
    origin = tile.get_rect().move(offset)
    for row in xrange(tileRows):
        for col in xrange(tileColumns):
            dest = origin.move(width * col, height * row)
            screen.blit(tile, dest)

# Update position of all the sprites and the scrolling background. Also perform
# some rudimentary edge of window collision detection on each sprite
def onUpdate():
    global camera

    # Bounce the balls around with simple edge of screen collision
    for i in xrange(balls):
        rect = spriteRect[i]
        speed = spriteSpeed[i]
        
        rect.move_ip(speed)
        if rect.left < 0 or rect.right > size.width:
            speed[0] = -speed[0]
        if rect.top < 0 or rect.bottom > size.height:
            speed[1] = -speed[1]

    # Update the camera's position using the current background scrolling speed
    # By making the offset "wrap around" under modulo arithmetic, we can get a
    # continuously repeating background pattern.
    width, height = tile.get_rect().width, tile.get_rect().height
    camera = (camera[0] + scroll[0]) % width, (camera[1] + scroll[1]) % height

# Draw the scrolling background and the sprites at their current locations
def onDraw():
    # First blit the background so it appears underneath all sprites
    drawBackground(camera)

    # Then blit every sprite at its current position
    for i in xrange(balls):
        screen.blit(ball, spriteRect[i])
    
# The try..finally block ensures that pygame.quit() is always called to close the
# main window. This is necessary when running under the IDLE Python GUI since the
# Python interpreter is not actually shutdown when this piece of code finishes
# or throws an exception.
try:

    # The size of the real screen surface will be selectable by the user to
    # be a multiple of 320x240. We also want to set the video mode first so
    # that any subsequent surfaces we create can be convert()ed to the same
    # pixel format as the display for maximum blit speed.
    pygame.display.set_caption("Pygame Speed Test")
    screen = pygame.display.set_mode(winsize, 0, 8)
    size = screen.get_rect()

    # Load the combined palette for all images into the display and intermediate
    # surfaces. All further Surface.convert() calls on other surface images will
    # remap the color indices to match the loaded palette as long as both
    # palette's have identical RGB triples somewhere. Note that we don't call
    # convert() on the palette image itself or we'd loose its color information.
    screen.set_palette(pygame.image.load("palette.png").get_palette())

    # Load all image resources
    tile = loadImage("tile.png")
    ball = loadImage("ball.png")

    # Setup a random scrolling speed for the background
    scroll = randomSpeed(2)
    camera = (0, 0)

    # Create some sprites with random positions and movement speeds
    spriteRect = [ randomRect(ball.get_rect()) for i in xrange(balls) ]
    spriteSpeed = [ randomSpeed(10) for i in xrange(balls) ]

    # Setup a timer object to maintain consistent frame rate
    timer = pygame.time.Clock()

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
        onUpdate()

        # Calculate and accumulate the total elapsed time to render each frame
        renderTicks += pygame.time.get_ticks() - startTicks

        # Every second the average rendering time is calculated and displayed
        # in the window's title bar as an absolute time and a percentage out of
        # the available time per frame. If the percentage goes over 100% we
        # start dropping frames and the animation slows down.
        frameCount += 1
        if frameCount >= timer.get_fps():
            average = float(renderTicks) / frameCount
            percent = (average * timer.get_fps()) / 10
            
            data = (size.width, size.height, average, percent, timer.get_fps())
            pygame.display.set_caption(caption % data)

            frameCount = 0
            renderTicks = 0

# Calling sys.exit() raises a SystemExit eception. This keeps it from propagating
# to the IDLE Python Shell window where it would get displayed otherwise.
except SystemExit:
    pygame.quit()
    
finally:
    pygame.quit()
