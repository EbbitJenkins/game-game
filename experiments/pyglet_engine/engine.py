#/usr/bin/env python

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
        self.bounds_x = bounds[0]       # List of x, y tuples of x bounds
        self.bounds_y = bounds[1]       # List of x, y tuples of y bounds
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
            sprite.update(cam_x, cam_y, self.bounds_x, self.bounds_y)

class Sprite:
    def __init__(self, x, y, weight):
        self.x, self.y = x, y
        self.dx, self.dy = 0, 0
        self.weight = weight    # For use with gravity
        self.image = pyglet.image.load('player.png')
        self.width, self.height = self.image.width, self.image.height

        # Is this sprite in the camera's view or not
        self.active = False 

        # Out of bounds?
        self.bound = {'up':False, 'down':False, 'left':False, 'right':False}

    def start_running(self, dx):
        self.dx = dx

    def stop_running(self):
        self.dx = 0

    def gravity(self):
        self.y -= self.weight


    def update(self, cam_x, cam_y, bounds_x, bounds_y):
        """
        Check the sprite's boundaries with the map's boundary data and update 
        the sprite's position on the map and blit it according to the camera's 
        relation with the map.
        """

        # TODO: This method could probably be a lot more efficient

        if not (self.x, self.y) in bounds_x:
            # Has not reached a vertical boundary
            self.x += self.dx
            self.bound['left'], self.bound['right'] = False, False
        else:
            if self.dx < 0:
                # Found a left boundary
                self.bound['left'] = True
            elif self.dx > 0:
                # Found a right boundary
                self.bound['right'] = True

        if not (self.x, self.y) in bounds_y:
            # Sprite has not reached a horizontal boundary
            self.y += self.dy
            self.gravity()
            self.bound['down'], self.bound['up'] = False, False
        else:
            if self.dy < 0:
                # Found a lower boundary
                self.bound['down'] = True
            elif self.dy > 0:
                # Found an upper boundary
                self.bound['up'] = True

        if self.dx < 0 and self.bound['right']:
            # At a right boundary but moving left, so it's ok
            self.x += self.dx

        if self.dx > 0 and self.bound['left']:
            # At a left boundary but moving right, so it's ok
            self.x += self.dx

        if self.dy < 0 and self.bound['up']:
            # At an upper boundary but moving down, so it's ok
            self.y += self.dy

        if self.dy > 0 and self.bound['down']:
            # At a lower boundary but moving up, so it's ok
            self.y += self.dy

        # Camera's x and y must be subtracted or the sprite would be moving at
        # double speed and out of the center of the camera's view.
        self.image.blit(self.x - cam_x - self.width / 2, self.y - cam_y)

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
            sprite.active = True if collide(self, sprite) else False

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
        self.sprite.update(self.x, self.y, self.map.bounds_x, self.map.bounds_y)

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

def process_boundary_data(data, t_width, t_height):
    """
    Parses the list of lists that represents the boundaries of the map and
    builds lists of pixes sprites can't cross.

    NOTE: This is probably a horrible way to do this.
    """
    v_bounds = []
    h_bounds = []

    i, j = 0, 0
    r = range(t_width) # THOSE LIST COMPREHENSIONS WILL STAY ONE LINE

    for y in data:
        for x in y:
            if x == '-' or x == '+':
                h_bounds += [(i * t_width + v, j * t_height) for v in r]

            if x == '|' or x == '+':
                v_bounds += [(i * t_width + v, j * t_height) for v in r]

            i += 1
        i = 0
        j += 1

    return v_bounds, h_bounds

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
    tile_layout.reverse()
    map_data.reverse()
    
    map_image = process_tile_data(tile_grid, tile_layout)

    width, height = tile_grid[0].width, tile_grid[0].height
    boundary_data = process_boundary_data(map_data, width, height)

    return Map(map_image, boundary_data)

if __name__ == '__main__':
    window = pyglet.window.Window()

    map = load_map('1.level')
    player = Sprite(320, 400, 2)
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
