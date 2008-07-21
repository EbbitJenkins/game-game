#!/usr/bin/env python

import sys
import pyglet
import itertools
from sprites import *
from pyglet.gl import *
from pyglet.window import key

# Command line arg fun
try:
    classname = sys.argv[1]
    spr = eval(classname)(100, 100)
except IndexError:
    print 'Usage: test_sprites.py sprite_classname [cycle_length_in_seconds]'
    print 'Example: test_sprites.py Arrow'
    exit()
except (NameError, TypeError):
    print 'Error: Sprite "' + classname + '" not found'
    exit()

try:
    cycle_length = int(sys.argv[2])
except IndexError:
    cycle_length = 1
    print 'Defaulting to 1 second between actions'

actions_iter = itertools.cycle(iter(spr.images))

def get_action_name(action):
    item = [k for k in spr.images.keys() if spr.images[k] == spr.image]

    return str(item[0])

def cycle_actions(dt):
    spr.image = spr.images[actions_iter.next()]
    action_text.text = get_action_name(spr.image)

def update(dt):
    background.blit(0, 0)
    spr.update()
    action_text.draw()

# Create a plain black background image
action_text = pyglet.text.Label(get_action_name(spr.image), x=20, y=20)
pattern = pyglet.image.SolidColorImagePattern((0, 0, 0, 100))
background = pattern.create_image(640, 480)

window = pyglet.window.Window(width=320, height=240)

# Turn on alpha transparency
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

# Run update at 20fps to simulate ThVortex's upcoming virtual frame rate stuff
pyglet.clock.schedule_interval(update, 1/20.0)
pyglet.clock.schedule_interval(cycle_actions, cycle_length)
pyglet.app.run()
