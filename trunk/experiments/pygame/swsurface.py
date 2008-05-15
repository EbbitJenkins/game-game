#!/bin/usr/env python

import sys, pygame

# Pygame 1.8.0 is missing the SDL_APPxxx bit flags!!!
pygame.APPMOUSEFOCUS = 0x01
pygame.APPINPUTFOCUS = 0x02
pygame.APPACTIVE = 0x04

# The constants used are as follows:
# bgsize: fixed size of the internal rendering surface before scaling
# speed: number of pixels by which the ball is moved per frame
# bgcolor: background color used to erase the internal rendering surface
# fps: the desired frames per second
bgsize = pygame.Rect(0, 0, 320, 240)
speed = [1, 1]
bgcolor = (50, 0, 0)
fps = 50

# The renderTicks variable accumulates the total number of milliseconds used to
# render each frame. The frameCount is used to display renderTicks in the windows
# title bar every second and to reset renderTicks. tickError is the maximum
# difference between the ideal 20ms delay between frames and the actual delay.
renderTicks = 0
frameCount = 0

# If another application's window is selected, this becomes False and the main
# event loop pauses by blocking on pygame.event.wait() until we regain input
# focus again. Since we never get an initial ACTIVEEVENT, this variable must
# be initialized to True.
hasInputFocus = True

# Dispatch a SDL event. Using the same function to handle events during a
# paused and an active game simplifies things.
def onEvent(event):

    # If the window is getting closed, then quit this shindig
    if event.type == pygame.QUIT:
        sys.exit()

    # If the window looses/gains input focus, update hasInputFocus
    elif event.type == pygame.ACTIVEEVENT:
        if event.state & pygame.APPINPUTFOCUS:
            global hasInputFocus
            hasInputFocus = bool(event.gain)

pygame.init()

# The try..finally block ensures that pygame.quit() is always called to close the
# main window. This is necessary when running under the IDLE Python GUI since the
# Python interpreter is not actually shutdown when this piece of code finishes
# or throws an exception.
try:

    # The size of the real screen surface will be selectable by the user to
    # always be either 320x240 or 640x480. For now we'll run it with 640x480
    # to stress test the thing. We also want to set the video mode first so
    # that any subsequent surfaces we create can be convert()ed to the same
    # pixel format as the display for maximum blit speed.
    pygame.display.set_caption("Speed Test:")
    screen = pygame.display.set_mode((640, 480))
    size = screen.get_rect()

    # All game graphics are internally drawn to a fixed sized intermediate
    # surface, which by default will have the same pixel format as the display.
    # If the window size was already 320x240, we could set "bg = screen" and
    # avoid the expense of the intermediate surface.
    bg = pygame.Surface(bgsize.size)

    # Load the sprite image and convert it to a format that matches the display
    # surface to get the maximum possible blit speed.
    ball = pygame.image.load("ball.png").convert()
    ballrect = ball.get_rect()

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

        # Bounce the ball around with simple edge of screen collision
        ballrect = ballrect.move(speed)
        if ballrect.left < 0 or ballrect.right > bgsize.width:
            speed[0] = -speed[0]
        if ballrect.top < 0 or ballrect.bottom > bgsize.height:
            speed[1] = -speed[1]

        # Blit the ball at current position to the internal screen surface
        bg.fill(bgcolor)
        bg.blit(ball, ballrect)

        # Scale the internal screen surface to the real window surface.
        # Since the scaling operation updates the entire screen surface, we
        # don't have to call screen.fill()
        pygame.transform.scale(bg, size.size, screen)

        # Calculate and accumulate the total elapsed time to render each frame
        renderTicks += pygame.time.get_ticks() - startTicks

        # Every second the average rendering time is calculated and displayed
        # in the window's title bar as an absolute time and a percentage out of
        # the available time per frame. If the percentage goes over 100% we
        # start dropping frames and the animation slows down.
        frameCount += 1
        if frameCount >= fps:
            average = float(renderTicks) / frameCount
            percent = (average * fps) / 10
            
            caption = "Speed Test: %.2fms (%2.1f%%)" % (average, percent)
            pygame.display.set_caption(caption)

            frameCount = 0
            renderTicks = 0


# Calling sys.exit() raises a SystemExit eception. This keeps it from propagating
# to the IDLE Python Shell window where it would get displayed otherwise.
except SystemExit:
    pygame.quit()
    
finally:
    pygame.quit()
