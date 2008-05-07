#!/bin/usr/env python

import sys, pygame

# Pygame 1.8.0 is missing a SDL constant!!!
pygame.APPACTIVE = 6

# The constants used are as follows:
# bgsize: fixed size of the internal rendering surface before scaling it to window
# speed: number of pixels by which the ball is moved per frame
# bgcolor: background color used for the window
# delay: delay between frames in milliseconds; 20ms = 50fps
bgsize = pygame.Rect(0, 0, 320, 240)
speed = [1, 1]
bgcolor = (50, 0, 0)
delay = 20

# The renderTicks variable accumulates the total number of milliseconds used to
# render each frame. The frameCount is used to display renderTicks in the windows
# title bar every second and to reset renderTicks.
renderTicks = 0
frameCount = 0

# If game window was minimized, pause until the window is restored. During a
# pause the recurring timer is disabled to minimize CPU usage. 
def pause():
    # Stop the frame timer
    pygame.time.set_timer(pygame.USEREVENT, 0)

    # Sleep idle until an ACTIVEEVENT reports the window is restored
    # All other events are discarded
    while True:
        event = pygame.event.wait()
        if event.type == pygame.ACTIVEEVENT:
            if event.state == pygame.APPACTIVE and event.gain:
                break
            
    # Restart the frame timer again
    pygame.time.set_timer(pygame.USEREVENT, delay)

pygame.init()

# The try..finally block ensures that pygame.quit() is always called to close the
# main window. This is necessary when running under the IDLE Python GUI since the
# Python interpreter is not actually shutdown when this piece of code finishes
# or throws an exception.
try:

    # The size of the real screen surface can change since the window is resizable.
    # Unfortunately, SDL/Pygame provides no way to limit or set the window size
    # from the program so we have to deal with maintaining the aspect ratio when
    # displaying the final result to the screen. We also want to set the video mode
    # first so that any subsequent surfaces we create can be convert()ed to the
    # same video mode as the display.
    pygame.display.set_caption("Speed Test:")
    screen = pygame.display.set_mode(bgsize.size, pygame.RESIZABLE)
    size = screen.get_rect()

    # All game graphics are internally drawn to a fixed sized intermediate surface.
    bg = pygame.Surface(size.size)

    # Load the sprite image and convert it to a format that matches the display
    # surface to get the maximum possible blit speed.
    ball = pygame.image.load("ball.png").convert()
    ballrect = ball.get_rect()

    # Setup a recurring timer for desired frame rate. This is the most accurate way
    # I found of maintaining a constant frame rate.
    pygame.time.set_timer(pygame.USEREVENT, delay)

    while True:
        
        # Sleep idle until either a timer event fires or the user manipulates
        # the game window in some manner. I decided that using an event queue to
        # defer event processing is overkill. This arrangement seems to produce
        # accurate enough timing as is.
        #
        # BUGS: While the user is resizing the window, Python is suspended until
        # the mouse button is released. However, the timer continues to fire and
        # generate events. If the user takes too long, the timer will have filled
        # up the entire event queue and then the VIDEORESIZE event will be lost.
        while True:
            event = pygame.event.wait()

            # If the frame timer fired, display the frame and update game logic
            if event.type == pygame.USEREVENT:
                break
            
            # If the window is getting closed, then quit this shindig
            elif event.type == pygame.QUIT:
                sys.exit()

            # If the window is resized, adjust screen surface to match
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                size = screen.get_rect()
            
            # If the window is minimized, pause the game
            elif event.type == pygame.ACTIVEEVENT:
                if event.state == pygame.APPACTIVE and not event.gain:
                    pause()

        # This will be used to measure how long it takes to render a frame
        startTicks = pygame.time.get_ticks()

        # Display the previously rendered frame before drawing the current
        # one. This ensures that any variation in rendering time (due to a
        # changing number of sprites) is not visible to the user.
        pygame.display.flip()

        # In case we missed some previous timer events, we don't want them to
        # accumulate (maybe another program temporarily tied up the CPU).
        pygame.event.clear(pygame.USEREVENT)

        # Bounce the ball around with simple edge of screen collision
        ballrect = ballrect.move(speed)
        if ballrect.left < 0 or ballrect.right > bgsize.width:
            speed[0] = -speed[0]
        if ballrect.top < 0 or ballrect.bottom > bgsize.height:
            speed[1] = -speed[1]

        # Blit the ball at current position to the internal screen surface
        bg.fill(bgcolor)
        bg.blit(ball, ballrect)

        # Smooth scale the internal screen surface to the real window surface
        # while maintaining the aspect ratio of the internal surface. It seems
        # the screen surface is automatically erased to black by each
        # pygame.displa.flip() so we can save some time by not having to do it
        # ourselves.
        #
        # NOTE: It is only possible to get a subsurface of the screen if the
        # display mode is not hardware accelerated (according to Pygame docs).
        fit = bgsize.fit(size)
        pygame.transform.smoothscale(bg, fit.size, screen.subsurface(fit))

        # Calculate and accumulate the total elapsed time to render each frame
        renderTicks += pygame.time.get_ticks() - startTicks

        # Every second the average rendering time is calculated and displayed
        # in the window's title bar as an absolute time and a percentage out of
        # the available time per frame. If the percentage goes over 100% we start
        # dropping frames and the animation slows down.
        frameCount += 1
        if frameCount >= 1000 / delay:
            average = float(renderTicks) / frameCount
            percent = (average / delay) * 100
            
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
