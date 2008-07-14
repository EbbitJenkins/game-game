import fsm
import state
import globals
import math

class Sprite(fsm.FSM):
    # creates all of the attributes describing the sprite's behavior
    def __init__(self, x, y):
        self.curr_state = STATE_null(self)          # For initializing internal FSM, must define own STATE_null to control flow
        self.images = self._load_images()           # gets a dictionary of sprite images
        self.image = None                           # sprite's current image
        self._width = 0                             # width of sprite
        self._height = 0                            # height of sprite
        self._buffer = 5                # used for collision
        self.active = False 	        # is sprite in camera?
        self.hp_max = 0                 # max hp sprite can have                
        self.hp = self.hp_max           # sprite's current hp
        self.d = {'x': 0, 'y': 0}       # directional vector
        self.x = x              # position on x-axis
        self.y = y              # position on y-axis
        self.weight = 0     	# How fast sprite falls
        self.gravity = 'south'  # Direction of gravity for sprite
        self.facing = 'west'    # Direction sprite is facing
        self._init()
    
    def _init(self):
        # Put custom initialization stuff here
        pass    

    def _load_images(self):
        images = {}
        return images
		
    def update(self, dt):
        self.do_state(self.curr_state.update(dt))
        
    def isCollision(self):
        # Computes boolean values for each of the 6 adjacent tiles
		# Returns whether or not spider can move in the directions specified in self.d['x'], self.d['y']

        # Since this sprite is 1x2 tiles, we need 4 x bounds
        #    n
        # nw P ne
        # sw P se
        #    s

        w, h = globals.tile_w, globals.tile_h
        x, y = self.x, self.y
        dx, dy = self.d['x'], self.d['y']
        #print "w, h: " + str(w) + ", " + str(h)
        #print "x, y: " + str(x) + ", " + str(y)
    
        bound_n  = self._dig(dx, dy, x, y, 0, "n")
        bound_s  = self._dig(dx, dy, x, y, 0, "s")
        bound_se = self._dig(dx, dy, x, y, 0, "se")
        bound_sw = self._dig(dx, dy, x, y, 0, "sw")
        bound_ne = self._dig(dx, dy, x, y, 0, "ne")
        bound_nw = self._dig(dx, dy, x, y, 0, "nw")

        # Might as well combine x directions
        bound_e = bound_se or bound_ne
        bound_w = bound_nw or bound_sw
        
        collision           = {"north": 0, "east": 0, "south": 0, "west": 0}
        

        # If the sprite is bound in a direction it is going, set that array position to false
        if (dy > 0 and bound_n):  
            collision["north"] = 1
        if (dx > 0 and bound_e):
            collision["east"] = 1
        if (dy < 0 and bound_s): 
            collision["south"] = 1
        if (dx < 0 and bound_w):
            collision["west"] = 1
            
        return collision
    def isGrounded(self):
        # used to see if it has walked off an edge, sorta hacky
        if globals.map.bounds[int((self.y - 1) / globals.tile_h)][int(self.x / globals.tile_w)] == '=':        
            return True
        else:
            return False
    
    def _dig(self, dx, dy, x, y, count, direction):
        # Directions = n, s, se, sw, ne, nw
        # Recursively checks for boundaries, pixel by pixel
        # SETS self.d['x'] or self.d['y'] to appropriate values to not go through walls - it should be OK to run this over and over to get booleans
        if direction == "n":
            # Checking to the north. If d['y'] > 0, then this could happen
            # bounds[y][x] returns True if that point is a collision
            if not globals.map.bounds[int((y + self._height) / globals.tile_h)][int(x / globals.tile_w)] == '=' and self.d['y'] > 0:
                # only check for as far as they are trying to move
                if count < math.fabs(dy):
                    # it is not a collision and we have not checked the entire move yet
                    collision = self._dig(dx, dy, x, y + 1, count + 1, direction)    # recursify!  Increment y by one to check the pixel above this one
                else:
                    # it is not a collision and we have checked all possible collision points, so there is no collision
                    collision = False   # Ends recursion
            else:
                # it is a collision
                if self.d['y'] > 0:
                    # they are trying to move in this direction
                    self.d['y'] = count     # count at this point is equal to the number of pixels it checked before it came to a wall.  If it moves this much, it will be exactly next to the wall.
                    collision = True    # Ends recursion
                else:
                    # not trying to move this direction
                    collision = False   # no recursion happens
            return collision            # Give back result
        if direction == "s":
            if not globals.map.bounds[int(y / globals.tile_h)][int(x / globals.tile_w)] == '=' and self.d['y'] < 0:
                if count < math.fabs(dy):
                    collision = self._dig(dx, dy, x, y - 1, count + 1, direction)
                else:
                    collision = False
            else:
                if self.d['y'] < 0:
                    self.d['y'] = -(math.fabs(count - 1))    # Since down is negative d['y']...
                    collision = True
                else:
                    collision = False
            return collision
        if direction == "se":
            if not globals.map.bounds[int(y / globals.tile_h)][int((x + self._width) / globals.tile_w)] == '=' and self.d['x'] > 0:
                if count < math.fabs(dx):
                    collision = self._dig(dx, dy, x + 1, y, count + 1, direction)
                else:
                    collision = False
            else:
                if self.d['x'] > 0:
                    self.d['x'] = count
                    collision = True
                else:
                    collision = False
            return collision
        if direction == "sw":
            if not globals.map.bounds[int(y / globals.tile_h)][int(x / globals.tile_w)] == '=' and self.d['x'] < 0:
                if count < math.fabs(dx):
                    collision = self._dig(dx, dy, x - 1, y, count + 1, direction)
                else:
                    collision = False
            else:				
                if self.d['x'] < 0:
                    self.d['x'] = -count
                    collision = True
                else:
                    collision = False
		return collision
        if direction == "ne":
            if not globals.map.bounds[int((y + self._height) / globals.tile_h)][int((x + self._width) / globals.tile_w)] == '=' and self.d['x'] > 0:
                if count < math.fabs(dx):
                    collision = self._dig(dx, dy, x + 1, y, count + 1, direction)
                else:                    
                    collision = False
            else:
                if self.d['x'] > 0:
                    self.d['x'] = count     
                    collision = True            
                else:
                    collision = False
            return collision
        if direction == "nw":
            if not globals.map.bounds[int((y + self._height) / globals.tile_h)][int(x / globals.tile_w)] == '=' and self.d['x'] < 0:
                if count < math.fabs(dx):
                    collision = self._dig(dx, dy, x - 1, y, count + 1, direction)
                else:
                    collision = False
            else:
                if self.d['x'] < 0:
                    self.d['x'] = -count
                    collision = True
                else:
                    collision = False
            return collision    
    def move(self):
        # actual drawing of the sprite will be handled elsewhere
        collision = self.isCollision()
        if not (collision['north'] or collision['south']):
            self.y = self.y + self.d['y']
        if not (collision['east'] or collision['west']):
            self.x = self.x + self.d['x']           

# sprite.SpriteState extends State
class SpriteState(state.State):
    def __init__(self, sprite):
        self._name = "null"     # Should be overwritten in subclass
        self._timer = 0
        self._sprite = sprite
# STATE_null is designed to be overwriten
class STATE_null(SpriteState):
    def __init__(self, sprite):
        self._name = "null"        
        self._sprite = sprite    
    def update(self, dt):
        return self     # You want to have this return your initial state
            
