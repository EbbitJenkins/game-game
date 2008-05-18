#/usr/bin/env python

import sys
import random
import pyglet                   # pyglet's sub-parts are lazy-loaded when called
from pyglet.gl import *         # Quick access to gl functions
from pyglet.window import key   # Quick access to key codes

class Map:
    """ 
    A map represents a level in the game. It holds all sprites that can appear
    on the map as well as information about the bounds in which the sprite can
    move.
    """

    def __init__(self, image, bounds):
        """
        Maps should be created with the load_map helper function.
        """

        self.image = image              # Background image created from tiles
        self.bounds = bounds            # 2D list of boundary tile types
        self.sprites = []               # Sprites on map
        self.width = self.image.width   # Shortcut
        self.height = self.image.height # Shortcut

    def crop(self, x, y, w, h):
        """
        Shortcut for getting a particular rectangle of the background. Used by
        the camera's make_view function.
        """

        return self.image.get_region(x, y, w, h)

    def update(self, cam_x, cam_y):
        """
        Updates all sprites on map.
        """

        # TODO: Seems kind of dirty to pass cam_x and cam_y two levels deep

        for sprite in self.sprites:
            sprite.update(cam_x, cam_y, self.bounds)

class Sprite:
    def __init__(self, x, y, weight):
        self.x, self.y = x, y
        self.dx, self.dy = 0, 0
        self.weight = weight    # For use with gravity
        self.images = self.load_images()
        self.image = self.images['stand_right']
        self.width, self.height = self.image.width, self.image.height
        self.falling = False
        self.start_gravity()

        # Is this sprite in the camera's view or not
        self.active = False 

    def load_images(self):
        images = {}

        images['stand_left'] = pyglet.image.load('marek-left.png')
        images['stand_right'] = pyglet.image.load('marek-right.png')

        return images

    def start_running(self, dx):
        self.dx = dx

        if dx > 0:
            self.image = self.images['stand_right']
        elif dx < 0:
            self.image = self.images['stand_left']

    def stop_running(self):
        self.dx = 0

    def gravity(self):
        self.y -= self.weight

    def start_gravity(self):
        self.falling = True
        self.dy = -self.weight

    def stop_gravity(self):
        self.falling = False
        self.dy = 0

    def reverse_gravity(self):
        self.y += self.weight

    def update(self, cam_x, cam_y, bounds):
        """
        Check the sprite's boundaries with the map's boundary data and update 
        the sprite's position on the map and blit it according to the camera's 
        relation with the map.
        """
        
        # For readability, whether or not the sprite is bound in a direction

        # Since this sprite is 1x2 tiles, we need 4 x bounds
        #    n
        # nw P ne
        # sw P se
        #    s

        bound_n  = bounds[(self.y + self.height + 17) / 16][self.x / 16] == '='
        bound_s  = bounds[(self.y - 1) / 16][self.x / 16] == '='
        bound_se = bounds[self.y / 16][(self.x + self.width + 1) / 16] == '='
        bound_sw = bounds[self.y / 16][(self.x - 1) / 16] == '='
        bound_ne = bounds[(self.y + 17)/16][(self.x + 1 + self.width)/16] == '='
        bound_nw = bounds[(self.y + 17) / 16][(self.x - 1) / 16] == '='

        # Might as well combine x directions
        bound_e = bound_se or bound_ne
        bound_w = bound_nw or bound_sw

        # If the sprite is not bound in the direction it wants to go in, let it
        if (self.dx > 0 and not bound_e) or (self.dx < 0 and not bound_w):
            self.x += self.dx

        if (self.dy > 0 and not bound_n) or (self.dy < 0 and not bound_s):
            self.y += self.dy

        # Camera's x and y must be subtracted or the sprite would be moving at
        # double speed and out of the center of the camera's view.
        self.image.blit(self.x - cam_x, self.y - cam_y)

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
        self.check_for_sprites()
        self.view.blit(0, 0)

        # Update all sprites in map
        self.map.update(self.x, self.y)

        # Update the sprite this camera is focusing on
        self.sprite.update(self.x, self.y, self.map.bounds)
 
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
            map_image.blit_into(grid[int(x) - 1], i * 16, j * 16, 0)
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
    Parse a level file into meaningful data. See 1.level for format. 

    NOTE: This format is what an editor should output, not a human.
          ...Unless you really dislike that human.
    """

    tileset_name, tile_str, coll_str = open(filename).read().split('\n\n')
    tileset_image = pyglet.image.load(tileset_name)
    tile_grid = pyglet.image.ImageGrid(tileset_image, 1, 8)
    tile_layout = [s.split(' ') for s in tile_str.split('\n')]
    map_data = [s.split(' ') for s in coll_str.split('\n')]
    map_data = map_data[:-1] if map_data[-1] == [''] else map_data
    
    map_image = process_tile_data(tile_grid, tile_layout)

    width, height = tile_grid[0].width, tile_grid[0].height
    bounds = process_bounds(map_data, width, height)

    return Map(map_image, bounds)

if __name__ == '__main__':
    window = pyglet.window.Window()

    try:
        map = load_map(sys.argv[1])
    except IndexError:
        print 'Please supply a level file (1.level or test.level)'
        exit()

    player = Sprite(320, 390, 2)
    camera = Camera(map, player, window.width, window.height)
    
    speed = 4
    dirs = {key.LEFT:-speed, key.RIGHT:speed}

    # Turn on alpha transparency
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def update(dt):
        camera.update()

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol in dirs.keys():
            player.start_running(dirs[symbol])

    @window.event
    def on_key_release(symbol, modifiers):
        if symbol in dirs.keys() and player.dx == dirs[symbol]:
            player.stop_running()

    pyglet.clock.schedule_interval(update, 1/60.0)  # Run update a 60 fps
    pyglet.app.run()
