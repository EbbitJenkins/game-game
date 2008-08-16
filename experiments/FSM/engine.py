#/usr/bin/env python

import globals
import sys                      # I need command line args
import random                   # For debug
import fsm						#Finite State Machine

import state_null               # State definitions
import state_intro              
import state_play
import state_exit
import state_menu
import state_death
import state_load

import pyglet                   # pyglet's sub-parts are lazy-loaded when called
from pyglet.gl import *         # Quick access to gl functions
from pyglet.window import key   # Quick access to key codes

# Used to access global level states
def STATE_null():
    return state_null.STATE_null("null")
    
def STATE_intro():
    return state_intro.STATE_intro("intro")
    
def STATE_play():
    return state_play.STATE_play("play")

def STATE_exit():
    return state_exit.STATE_exit("exit")

def STATE_menu():
    return state_menu.STATE_menu("menu")

def STATE_death():
    return state_death.STATE_death("death")
    
def STATE_load():
    return state_load.STATE_load("load")

class Map:
    """ 
    A map represents a level in the game. It holds all sprites that can appear
    on the map as well as information about the bounds in which the sprite can
    move.
    """

    def __init__(self, image, bounds, win_w, win_h):
        """
        Maps should be created with the load_map helper function.
        """

        self.image = image              # Background image created from tiles
        self.bounds = bounds            # 2D list of boundary tile types
        self.win_w = win_w              # Window width TODO: DIRTY?
        self.win_h = win_h              # Window height TODO: DIRTY?
        self.sprites = []               # Sprites on map
        self.width = self.image.width   # Shortcut
        self.height = self.image.height # Shortcut

    def crop(self, x, y, w, h):
        """
        Shortcut for getting a particular rectangle of the background. Used by
        the camera's make_view function.
        """

        return self.image.get_region(x, y, w, h)
class Camera:
    """
    Watches a part of the map and controls what it blitted on the screen
    depending upon what is in it's view.
    """

    def __init__(self, map, sprite, width, height):
        self.map = map          # Map to watch
        self.sprite = sprite    # Sprite to follow

        # Width and height will most likely be the same as the window.
        self.width = width 
        self.height = height

    def center(self):
        """
        Center the camera on the sprite that it is following
        """

        self.x = self.sprite.x - self.sprite.width / 2 - self.width / 2
        self.y = self.sprite.y - self.sprite.height / 2 - self.height / 2

        # Fix to the map's natural boundaries
        if self.x < 0:
            self.x = 0

        if self.x > self.map.width - self.width:
            self.x = self.map.width - self.width

        if self.y < 0:
            self.y = 0

        if self.y > self.map.height - self.height:
            self.y = self.map.height - self.height

    def make_view(self):
        """
        Grab the relevant part of the map to show.
        """

        self.view = self.map.crop(self.x, self.y, self.width, self.height)

    def check_for_sprites(self):
        """
        Find which sprites are in the camera's view.

        NOTE: Originally the camera held the list of active sprites, but I
        decided that it didn't make very much sense that way. A map has sprites,
        not a camera. I could be horribly wrong.
        """

        # TODO: Untested

        for sprite in map.sprites:
            sprite.active = bool(collide(self, sprite))

    def update(self):
        """
        Make camera's view accurate in relation to the sprite it is focusing.
        Also find any sprites that are new to the camera's view or that need to
        be removed.
        """

        self.center()
        self.make_view()
        #self.check_for_sprites()
        self.view.blit(0, 0)

		# Camera's x and y must be subtracted or the sprite would be moving at
        # double speed and out of the center of the camera's view.
        globals.marek.image.blit(globals.marek.x - self.x, globals.marek.y - self.y)
        for spider in globals.spiders:
            spider.image.blit(spider.x, spider.y)
        for bullet in globals.bullets:
            bullet.image.blit(bullet.x, bullet.y)
 
def collide(a, b):
    if a.y + a.height < b.y:
        return False
    if a.y > b.y + b.height:
        return False
    if a.x + a.width < b.x:
        return False
    if a.x > b.x + b.width:
        return False

    return True

def process_tile_data(grid, layout):
    """
    Creates a map image from parsable tiledata and a tileset grid.
    Takes an ImageGrid of the soon-to-be map's tileset and a list of lists
    representing which tiles go where on the map. The appropriate tile images
    are blitted one by one onto the map image.
    """

    layout.reverse()

    width = grid[0].width * len(layout[0])
    height = grid[0].height * len(layout)

    map_image = pyglet.image.Texture.create(width, height)
    i, j = 0, 0

    for y in layout:
        for x in y:
            map_image.blit_into(grid[int(x) - 1], i * tile_w, j * tile_h, 0)
            i += 1
        i = 0
        j += 1

    return map_image

def process_bounds(data, tile_w, tile_h):
    """
    In the initial implementation of this engine, this function made one-pixel
    barriers on the map that sprites could not cross. That was scrapped for
    creating horizontal and vertical rectangles that the sprite would collide
    with to create boundaries. In this latest implementation I am looking
    directly at the ASCII in the input file, so all I need to do is reverse
    the data so I can treat it as (y, x) coords. I don't like that its (y, x)
    rather than (x, y). Also we will probably want to make boundary data a 
    list of tile subclasses that you can access by (x, y) once we need to do
    more with them.
    """

    data.reverse()

    return data

def load_map(filename):
    """
    Parse a level file into meaningful data. See *.level for format. 

    NOTE: This format is what an editor should output, not a human.
          ...Unless you really dislike that human.
    """
    
    global tile_w, tile_h

    # Read metadata, tile_layer, and boundary_layer section of map file
    meta, tile_str, coll_str = open(filename).read().split('\n\n')

    # Split metadata into meaningful parts
    tileset_name, tile_w, tile_h, win_w, win_h = meta.split(' ')
    tile_w, tile_h = int(tile_w), int(tile_h)

    # Load tileset image and derive rows/cols amounts for imageGrid
    tileset_image = pyglet.image.load(tileset_name)
    rows, cols = tileset_image.height / tile_w, tileset_image.width / tile_h
    tile_grid = pyglet.image.ImageGrid(tileset_image, rows, cols)

    # Create a map image from tile data
    tile_layout = [s.split(' ') for s in tile_str.split('\n')]
    map_data = [s.split(' ') for s in coll_str.split('\n')]
    map_data = map_data[:-1] if map_data[-1] == [''] else map_data
    map_image = process_tile_data(tile_grid, tile_layout)

    # Create meaningful bounds data from ascii grid
    bounds = process_bounds(map_data, tile_w, tile_h)
    
    # set global info
    globals.tile_w = tile_w
    globals.tile_h = tile_h

    return Map(map_image, bounds, int(win_w), int(win_h))

def load_image(filename):
	return pyglet.image.load(filename)

if __name__ == '__main__':
    tile_w, tile_h = None, None
    try:
        globals.map = load_map(sys.argv[1])
        pass
    except IndexError:
		print 'Please supply a level file (big1.level, big2.level, small.level)'
		exit()
    try:
        globals.spider_number = sys.argv[2]
    except IndexError:
        print 'Please supply a number of spiders to spawn after the level file (1, 5, 50, etc)'
        exit()        
    globals.window = pyglet.window.Window(width=globals.map.win_w, height=globals.map.win_h)
    fsm = fsm.FSM(STATE_null())   # Initialize the global Finite State Machine

    # Turn on alpha transparency
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def update(dt):        
		fsm.do_state(fsm.curr_state.update(dt))

    @globals.window.event
    def on_key_press(symbol, modifiers):
        if symbol == key.LEFT:
            print "key.LEFT PRESSED"
            globals.marek.dx = -globals.marek.run_speed
            print "globals.marek.dx: " + str(globals.marek.dx)
        elif symbol == key.RIGHT:
            print "key.RIGHT PRESSED"
            globals.marek.dx = globals.marek.run_speed
            print "globals.marek.dx: " + str(globals.marek.dx)
        elif symbol == key.SPACE:
            print "key.SPACE PRESSED"
            if not globals.marek.move_state.curr_state.__doc__ == "jump":                
                print "marek.move_state is not jump"
                globals.marek.move_state.action = globals.marek.moves.STATE_jump()

    @globals.window.event
    def on_key_release(symbol, modifiers):
        if symbol == key.LEFT:
            print "key.LEFT RELEASED"
            globals.marek.dx = 0
        elif symbol == key.RIGHT:
            print "key.RIGHT RELEASED"
            globals.marek.dx = 0        
        elif symbol == key.SPACE:
            print "key.SPACE RELEASED"
            globals.marek.move_state.action = globals.marek.moves.STATE_fall()
        elif symbol == key.UP:
            print "marek x, y: " + str(globals.marek.x) + ", " + str(globals.marek.y)
            print "spider x, y: " + str(globals.spider.x) + ", " + str(globals.spider.y)

    pyglet.clock.schedule(update)  # Run update on every vsync
    pyglet.app.run()
