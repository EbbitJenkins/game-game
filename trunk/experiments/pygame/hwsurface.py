#!/bin/usr/env python

import sys, pygame, random

# Pygame 1.8.0 is missing the SDL_APPxxx bit flags!!!
pygame.APPMOUSEFOCUS = 0x01
pygame.APPINPUTFOCUS = 0x02
pygame.APPACTIVE = 0x04

# The background color used to erase the internal rendering surface
bgcolor = (50, 0, 0)

# The frameCount is used to update the window title bar every second with the
# number of fps. To view the title bar, it is necessary to minimize the program
# and look at the task bar.
frameCount = 0

# If another application's window is selected, this becomes False and the main
# event loop pauses by blocking on pygame.event.wait() until we regain input
# focus again. Since we never get an initial ACTIVEEVENT, this variable must
# be initialized to True.
hasInputFocus = True

# (Re)Initialize all SDL surfaces. When using DirectDraw under Windows, if an
# application is minimized and then restored, all of the display surfaces are
# lost and must be recreated again.
def onInit():
    global image
    
    # Load the sprite image, stretch it to half the size of the background,
    # and convert it to a format that matches the display surface to get the
    # maximum possible blit speed.
    image = pygame.image.load("ball.png").convert()
    image = pygame.transform.scale(image, (bgsize.width / 2, bgsize.height / 2))

# Dispatch a SDL event. Using the same function to handle events during a
# paused and an active game simplifies things.
def onEvent(event):
    global hasInputFocus

    # If the window is getting closed, then quit this shindig
    if event.type == pygame.QUIT:
        sys.exit()

    # The window menu in the taskbar doesn't seem to work for a minimized
    # fullscreen app under Windows, so we also let the user hit ESC to exit
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        sys.exit()

    # If the window looses/gains input focus, update hasInputFocus
    # If the window is un-minimized, all surfaces have to be reloaded
    elif event.type == pygame.ACTIVEEVENT:
        if event.state & pygame.APPINPUTFOCUS:
            hasInputFocus = bool(event.gain)
        if event.state & pygame.APPACTIVE and event.gain:
            onInit()

random.seed()
pygame.init()

# The try..finally block ensures that pygame.quit() is always called to close the
# main window. This is necessary when running under the IDLE Python GUI since the
# Python interpreter is not actually shutdown when this piece of code finishes
# or throws an exception.
try:

    # Get the list of supported video resolutions
    modes = pygame.display.list_modes()

    # Switch to the highest supported video resolution.
    # We also want to set the video mode first so that any subsequent surfaces
    # we create can be convert()ed to the same pixel format and HWSURFACE as
    # the display for maximum blit speed.
    pygame.mouse.set_visible(False)
    pygame.display.set_caption("Speed Test:")

    bg = pygame.display.set_mode(modes[0],
        pygame.HWSURFACE | pygame.FULLSCREEN | pygame.DOUBLEBUF)
    bgsize = bg.get_rect()
    print "Using max resolution %dx%d" % bgsize.size

    if not bg.get_flags() & pygame.HWSURFACE:
        raise "No hardware acceleration. Try setting SDL_VIDEODRIVER?"    

    # Load sprite images
    onInit()

    # Create a bunch of balls at random location and moving in random directions  
    balls = []
    sprite = image.get_rect()
    for i in xrange(10):
        x = random.randrange(bgsize.width - sprite.width)
        y = random.randrange(bgsize.height - sprite.height)
        d = range(1, 10) + range(-1, -10, -1)
        speed = [random.choice(d), random.choice(d)]
        balls.append([sprite.move(x, y), speed])

    # Setup a timer object to measure the frame rate
    timer = pygame.time.Clock()

    while True:
        
        # Poll for any pending events in the main loop
        for event in pygame.event.get():
            onEvent(event)

        # If we need to pause, block on event loop until we get focus back
        while not hasInputFocus:
            onEvent(pygame.event.wait())

        # This will determine the average frame rate we're running at
        timer.tick()
        fps = timer.get_fps()

        # Display the previously rendered frame before drawing the current
        # one. On a HWSURFACE with DOUBLEBUF the flip() is synchronized to
        # vsync. This makes a frame limiting timer unnecessary. At least on
        # my system, SDL/DirectView seems to delay some operations until the
        # pygame.display.flip() which makes it difficult to estimate how much
        # time is spent each frame on drawing. Also, the flip() seems to do
        # a busy wait for vsync which drivers the cpu load up to 99%.
        pygame.display.flip()

        # Bounce the balls around with simple edge of screen collision
        for ball in balls:
            ballrect = ball[0]
            speed = ball[1]
            
            ballrect.move_ip(speed)
            if ballrect.left < 0 or ballrect.right > bgsize.width:
                speed[0] = -speed[0]
            if ballrect.top < 0 or ballrect.bottom > bgsize.height:
                speed[1] = -speed[1]

        # Blit the balls at current position to the internal screen surface
        bg.fill(bgcolor)
        for ball in balls:
            bg.blit(image, ball[0])

        # Every second the average rendering time is calculated and displayed
        # in the window's title bar as an absolute time and a percentage out of
        # the available time per frame. If the percentage goes over 100% we
        # start dropping frames and the animation slows down.
        frameCount += 1
        if frameCount >= fps:
            caption = "Speed Test: %d fps" % fps
            pygame.display.set_caption(caption)
            frameCount = 0

# Calling sys.exit() raises a SystemExit eception. This keeps it from propagating
# to the IDLE Python Shell window where it would get displayed otherwise.
except SystemExit:
    pygame.quit()
    
finally:
    pygame.quit()
