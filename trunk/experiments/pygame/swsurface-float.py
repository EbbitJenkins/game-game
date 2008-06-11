#!/usr/bin/env python

import sys, pygame, random

# Pygame 1.8.0 is missing the SDL_APPxxx bit flags!!!
pygame.APPMOUSEFOCUS = 0x01
pygame.APPINPUTFOCUS = 0x02
pygame.APPACTIVE = 0x04

# The constants used are as follows:
# winsize: initial display size for the window
# balls: the number of bouncing sprites to create
# fps: the desired display frame rate per second 
# speedup: overall speedup or slowdown factor
winsize = (640, 480)
balls = 100
fps = 100
speedup = 1.0

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
caption = "%dx%d    Draw: %.2fms (%2.1f%%)    Disp: %2.1ffps    Speed: %1.1fx"

# Dispatch a SDL event. Using the same function to handle events during a
# paused and an active game simplifies things.
def onEvent(event):
    global fps, speedup, prevFrameTicks, hasInputFocus

    # If the window is getting closed, then quit this shindig
    if event.type == pygame.QUIT:
        sys.exit()

    # If the ESC key was hit, then also quit this shindig
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        sys.exit()

    # If the "i" key was hit, then toggle interpolation flag
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
        hasInterpolation = not hasInterpolation

    # If PgUp or PgDn hit, adjust real display rate
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEUP:
        fps += 1
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEDOWN:
        if fps > 1:
            fps -= 1

    # If + or - hit, adjust the virtual frame rate
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_EQUALS:
        speedup += 0.1
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_MINUS:
        if speedup >= 0.2:
            speedup -= 0.1
        
    # If user resized window, then re-scale all graphics
    elif event.type == pygame.VIDEORESIZE:
        onResize(event.size)

    # If the window looses/gains input focus, start and stop the frame
    # timer. When regaining focus, also reset the prevFrameTicks to
    # current time, otherwise the main game loop will attempt to catch
    # up all the virtual frames mised during the pause.
    elif event.type == pygame.ACTIVEEVENT:
        if event.state & pygame.APPINPUTFOCUS:
            hasInputFocus = bool(event.gain)
            prevFrameTicks = pygame.time.get_ticks()

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
    screen.set_palette(pygame.image.load("palette.png").get_palette())

    # The ratio between the display window size and the reference 320x240
    # resolution is used for scaling all game images and movement speeds. For
    # the most accurate scaling, the window size should be an integer multiple
    # of 320x240.
    ratio = float(bgsize.width) / refsize[0], float(bgsize.height) / refsize[1]

    # Load all image resources
    tileImage, tileSize = loadImage("tile.png")
    ballImage, ballSize = loadImage("ball.png")

    # Pre-render the background tile map
    bg = initBackground()

# Given a (x, y) tuple in the reference 320x240 coordinate space, return a new
# tuple that is scaled to match the actual window size. For the most accurate
# scaling, the window size should be an integer multiple of 320x240. This is
# function is used to scale images and coordinates.
def scale((x,y)):
    return int(round(x * ratio[0])), int(round(y * ratio[1]))

# Load a sprite/game image and pre-scale it to match the output display surface.
# It turns out that the Surface.blit() routines are so optimized it's more
# efficient to pre-scale and blit at the full resolution, even when blitting
# overlapping areas, then it would be to blit at 320x240 to an intermediate
# surface and then scale the entire display in realtime. This routine also
# reindexes the images palette indices of the loaded image with
# Surface.convert(). Also returns the size of the original image which is
# used by the game logic to remain independant of the actual screen size.
def loadImage(filename):
    image = pygame.image.load(filename).convert()
    size = image.get_size()
    
    newsize = scale(size)
    newimage = pygame.transform.scale(image, newsize)

    # Enabling run length encoding of the color key transparency map on a
    # SWSURFACE will slightly increase the blit speed when using this surface
    # as a blit source. The more transparent area that an image has, the more
    # pronounced the speed up will be.
    newimage.set_colorkey(newimage.get_colorkey(), pygame.RLEACCEL)
    
    return newimage, size

# Return random [x, y] list that can be used as a sprite/camera movement
# speed. The returned x and y values are in the range of "-speed/50.0" to
# "speed/50.0", excluding 0. The division by 50.0 accounts for the fact that
# in onUpdate() this speed is multiplied by the elapsed time (in miliseconds)
# between frames.
def randomSpeed(speed):
    values = range(1, speed, 1)
    values += range(-1, -speed, -1)
    return [random.choice(values) / 50.0, random.choice(values) / 50.0]

# Return a new [x, y] position randomly positioned within the reference 320x240
# area such that the rect defined by (width, height) still remains completely
# visible. The new position is suitable for use as a random starting location
# for sprites.
def randomPos((width, height)):
    x = float(random.randrange(refsize[0] - width))
    y = float(random.randrange(refsize[1] - height))
    return [x, y]

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
    global camera, spritePos, spriteSpeed

    # Bounce the balls around with simple edge of screen collision
    for i in xrange(balls):
        pos = spritePos[i]
        speed = spriteSpeed[i]
        
        # We can no longer simply toggle the speed between positive and negative
        # because we can't depend on how far the ball actually moved per frame
        pos[0], pos[1] = pos[0] + dt * speed[0], pos[1] + dt * speed[1]
        if pos[0] < 0:
            speed[0] = abs(speed[0])
        if pos[1] < 0:
            speed[1] = abs(speed[1])
        if pos[0] + ballSize[0] > refsize[0]:
            speed[0] = -abs(speed[0])
        if pos[1] + ballSize[1] > refsize[1]:
            speed[1] = -abs(speed[1])

    # Update the camera's position using the current background scrolling speed.
    # By making the offset "wrap around" under modulo arithmetic, we can get a
    # continuously scrolling background pattern.
    width, height = tileSize
    speed = dt * scroll[0], dt * scroll[1]
    camera = (camera[0] + speed[0]) % width, (camera[1] + speed[1]) % height

# Draw the scrolling background and the sprites at their current locations.
# The camera and sprite locations are scaled up from their logical 320x240
# coordinates to match the actual window size.
def onDraw():
    # First blit the background so it appears underneath all sprites
    drawBackground(scale(camera))

    # Blit every sprite at its current position
    for i in xrange(balls):
        screen.blit(ballImage, scale(spritePos[i]))
    
# The try..finally block ensures that pygame.quit() is always called to close the
# main window. This is necessary when running under the IDLE Python GUI since the
# Python interpreter is not actually shutdown when this piece of code finishes
# or throws an exception.
try:
    pygame.display.set_caption("Pygame Speed Test")

    # The size of the real screen surface will be selectable by the user to
    # be a multiple of 320x240. We also want to set the video mode first so
    # that any subsequent surfaces we create can be convert()ed to the same
    # pixel format as the display for maximum blit speed.
    onResize(winsize)

    # Setup a random scrolling speed for the background
    scroll = randomSpeed(2)
    camera = (0, 0)

    # Create some sprites with random positions and movement speeds
    spriteSpeed = [ randomSpeed(4) for i in xrange(balls) ]
    spritePos = [ randomPos(ballSize) for i in xrange(balls) ]

    # Setup a timer object to maintain consistent frame rate
    timer = pygame.time.Clock()

    # Used to keep track of elapsed time between each frame
    prevFrameTicks = pygame.time.get_ticks()

    while True:

        # Poll for any pending events in the main loop
        for event in pygame.event.get():
            onEvent(event)

        # If we need to pause, block on event loop until we get focus back
        while not hasInputFocus:
            onEvent(pygame.event.wait())

        # This will idle sleep to maintain the desired frame rate. Note that
        # since there is no vsync on SWSURFACEs, if the frame rate is too close
        # to the monitor's refresh rate (or an integer multiple of the refresh),
        # it will result in jerky animation.
        timer.tick(fps)

        # This will be used to measure how long it takes to render a frame
        startTicks = pygame.time.get_ticks()

        # Display the previously rendered frame before drawing the current
        # one. This ensures that any variation in rendering time (due to a
        # changing number of sprites) is not visible to the user.
        pygame.display.flip()

        # Calculate the elpased time between the previous frame and this one
        curFrameTicks = pygame.time.get_ticks()
        dt = curFrameTicks - prevFrameTicks
        prevFrameTicks = curFrameTicks

        # Update the positions of the camera and all sprites based on the
        # elapsed real time between frames (i.e. the delta time)
        onUpdate(dt * speedup)
        onDraw()

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
            
            data = (bgsize.width, bgsize.height, average, percent,
                    timer.get_fps(), speedup)
            pygame.display.set_caption(caption % data)
            #print(caption % data)

            frameCount = 0
            renderTicks = 0

# Calling sys.exit() raises a SystemExit exception. This keeps it from propagating
# to the IDLE Python Shell window where it would get displayed otherwise.
except SystemExit:
    pygame.quit()
    
finally:
    pygame.quit()
