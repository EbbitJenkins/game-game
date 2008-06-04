#/usr/bin/env python

import sys                      # I need command line args
import random                   # For debug
import pyglet                   # pyglet's sub-parts are lazy-loaded when called
from pyglet.gl import *         # Quick access to gl functions
from pyglet.window import key   # Quick access to key codes

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
        self.facing = 1 # TODO: Doc
        self.width, self.height = self.image.width, self.image.height
        self.jumping = False
        self.jump_length = 16
        self.bullets = []
        self.start_gravity()

        # Is this sprite in the camera's view or not
        self.active = False 

    def load_images(self):
        images = {}

        images['stand_left'] = pyglet.image.load('marek-left.png')
        images['stand_right'] = pyglet.image.load('marek-right.png')

        return images

    def shoot(self):
        self.bullets.append(Bullet(self.x, self.y + 13, self.facing))

    def start_running(self, dx):
        self.dx = dx

        if dx > 0:
            self.image = self.images['stand_right']
            self.facing = 1
        elif dx < 0:
            self.image = self.images['stand_left']
            self.facing = -1

    def stop_running(self):
        self.dx = 0

    # TODO: Probably shouldn't have to stop gravity here?
    def start_jumping(self):
        """
        Reset jump timer, stop gravity, and set jumping to true 
        """

        tmp = range(1, self.jump_length)
        tmp.reverse()
        tmp2 = [-x for x in range(1, self.jump_length)]
        self.jump_timer = iter(tmp + tmp2)
        self.stop_gravity()
        self.jumping = True

    def continue_jump(self):
        """
        Called when sprite is updated to change dy or stop jumping
        """

        try:
            self.dy = self.jump_timer.next() / 2
        except StopIteration:
            self.stop_jumping()

    def stop_jumping(self):
        """
        End jump, restart gravity
        """

        self.jumping = False 
        self.start_gravity()

    def start_gravity(self):
        self.dy = -self.weight

    def stop_gravity(self):
        self.dy = 0

    def update(self, cam_x, cam_y, bounds):
        """
        Check the sprite's boundaries with the map's boundary data and update 
        the sprite's position on the map and blit it according to the camera's 
        relation with the map.
        """

        # Handle jumping
        if self.jumping:
            self.continue_jump()
        
        # For readability, whether or not the sprite is bound in a direction

        # Since this sprite is 1x2 tiles, we need 4 x bounds
        #    n
        # nw P ne
        # sw P se
        #    s

        w, h = tile_w, tile_h

        bound_n  = bounds[(self.y + self.height + 1) / h][self.x / w] == '='
        bound_s  = bounds[(self.y - 1) / h][self.x / w] == '='
        bound_se = bounds[self.y / h][(self.x + self.width + 1) / w] == '='
        bound_sw = bounds[self.y / h][(self.x - 1) / w] == '='
        bound_ne = bounds[(self.y + h+1)/h][(self.x + 1 + self.width)/w] == '='
        bound_nw = bounds[(self.y + h + 1) / h][(self.x - 1) / w] == '='

        # Might as well combine x directions
        bound_e = bound_se or bound_ne
        bound_w = bound_nw or bound_sw

        # Prevents getting stuck in lower tile after jump
        if bound_s and self.y % tile_h:
            self.y += 16 - self.y % 16

        # If the sprite is not bound in the direction it wants to go in, let it
        if (self.dx > 0 and not bound_e) or (self.dx < 0 and not bound_w):
            self.x += self.dx

        if (self.dy > 0 and not bound_n) or (self.dy < 0 and not bound_s):
            self.y += self.dy

        # Update bullets
        for bullet in self.bullets:
            bullet.update(cam_x, cam_y)

            if bullet.timer > camera.width:
                self.bullets.remove(bullet)

        # Camera's x and y must be subtracted or the sprite would be moving at
        # double speed and out of the center of the camera's view.
        self.image.blit(self.x - cam_x, self.y - cam_y)

class Bullet:
    def __init__(self, x, y, dir):
        self.x, self.y = x, y
        self.dx, self.dy = dir * 8, 0
        self.timer = 0
        self.image = pyglet.image.load('bullet.png').get_texture()

        if dir < 0:
            self.x += 10
            self.image = self.image.get_transform(flip_x=True)
    
    def update(self, cam_x, cam_y):
        self.x, self.y = self.x + self.dx, self.y + self.dy
        self.timer += abs(self.dx)
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

    # Disable smooth scaling of map tiles. To get smooth scaling just comment
    # out the two lines below.
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

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

    return Map(map_image, bounds, int(win_w), int(win_h))

if __name__ == '__main__':
    tile_w, tile_h = None, None

    # Get map arg
    try:
        map = load_map(sys.argv[1])
    except IndexError:
        print 'Please supply a level file (big1.level, big2.level, small.level)'
        exit()

    window = pyglet.window.Window(width=map.win_w, height=map.win_h,
                                  resizable=True)

    # If the window size becomes zero in either dimension, we start getting
    # OpenGL errors on stdout. In the real game, this would probably be set
    # to the visible map size to prevent running at a smaller size than the
    # base map size.
    window.set_minimum_size(1, 1)
    
    player = Sprite(160, 120, 4)
    camera = Camera(map, player, map.win_w, map.win_h)
    
    speed = 4
    dirs = {key.LEFT:-speed, key.RIGHT:speed}

    # Turn on alpha transparency
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def update(dt):
        # By default Pyglet sets glOrtho() to match the current window size.
        # Setting it to the map size ensures that the same portion of the map
        # is always visible and that it is scaled to the window.
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, map.win_w, 0, map.win_h, -1, 1)
        glMatrixMode(GL_MODELVIEW)

        # Disable smooth scaling of sprites. To get smooth scaling just comment
        # out the two lines below.
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        # If smooth scaling is enabled, this prevents artifacts from appearing
        # around the edges of the sprites due to floating point rounding errors
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
                
        camera.update()

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol in dirs.keys():
            player.start_running(dirs[symbol])
        elif symbol == key.SPACE or symbol == key.Z:
            player.start_jumping()
        elif symbol == key.X:
            player.shoot()

    @window.event
    def on_key_release(symbol, modifiers):
        if symbol in dirs.keys() and player.dx == dirs[symbol]:
            player.stop_running()

    pyglet.clock.schedule_interval(update, 1/60.0)  # Run update a 60 fps
    pyglet.app.run()
