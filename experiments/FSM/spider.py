import globals
import spider_ai
import spider_move
import fsm
import engine
import math


# SPIDER
# A mechanical spider than hops around and can attach to walls and
# ceilings. It's annoying enough not to require its own weapon, and it's
# lightly armored so one shot kills it. It moves at a comparable speed
# to Marek walking.
#
# Note: that is the plan, not the reality at this point
# ----------------------------------------------------------------------------------------
class spider:
    # creates all of the attributes describing the sprite's behavior
    def __init__(self, x, y, weight):
        self.curr_state = STATE_null(self)          # initializes the state for the spider's FSM
        self.move_state = spider_move.move(self)    # initializes spider movement FSM
        self.moves = moves()    # used to access list of move states
        self.ai_state = spider_ai.ai(self)          # initializes spider AI FSM
        self.ais = ais()         # used to access list of AI states
        self.images = self.load_images()
        self.image = self.images['stand_right']
        self.width, self.height = self.image.width, self.image.height
        self.buffer = 5         # used for collision
        self.active = False 	# is in camera?
        self.hp = 100           # spider's current hp
        self.hp_max = 100       # max hp spider currently can have
        self.lives = 1          # times that spider can die
        self.dx = 0             # directional x-vector, max 1, min -1
        self.dy = 0             # directional y-vector, max 1, min -1
        self.x = x              # position on x-axis
        self.y = y              # position on y-axis
        self.weight = weight	# how fast spider falls
        self.run_speed = 1      # how fast spider runs
        self.run_length = 1     # how long spider walks in each direction
        self.jump_speed = self.weight * 3.0  # how fast spider ascends/descends when he jumps or falls
        self.jump_height = 0.5    # how long spider can jump for, in seconds
        self.jump_arc = 2       # how fast spider can move in x-axis while jumping or falling
        self.gravity = 'south'  # which direction is falling
        self.facing = 'west'    # which direction it is facing

    def load_images(self):
        images = {}
        images['stand_left'] = engine.load_image('spider.png')
        images['stand_right'] = engine.load_image('spider.png')
        return images
		
    def update(self, dt):
        # runs the spider FSM
        self.do_state(self.curr_state.update(dt))
        
    def do_state(self, next_state):
        if not (next_state == self.curr_state):
            self.curr_state.leave()
            
            self.curr_state = next_state
            
            self.curr_state.enter()
        return self.curr_state

    def isCollision(self):
        # Computes boolean values for each of the 6 adjacent tiles
		# Returns whether or not spider can move in the directions specified in self.dx, self.dy

        # Since this sprite is 1x2 tiles, we need 4 x bounds
        #    n
        # nw P ne
        # sw P se
        #    s

        w, h = globals.tile_w, globals.tile_h
        x, y = self.x, self.y
        dx, dy = self.dx, self.dy
        #print "w, h: " + str(w) + ", " + str(h)
        #print "x, y: " + str(x) + ", " + str(y)

        bound_n  = self.dig(dx, dy, x, y, 0, "n")
        bound_s  = self.dig(dx, dy, x, y, 0, "s")
        bound_se = self.dig(dx, dy, x, y, 0, "se")
        bound_sw = self.dig(dx, dy, x, y, 0, "sw")
        bound_ne = self.dig(dx, dy, x, y, 0, "ne")
        bound_nw = self.dig(dx, dy, x, y, 0, "nw")

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
    
    def dig(self, dx, dy, x, y, count, direction):
        # Directions = n, s, se, sw, ne, nw
        # Recursively checks for boundaries, pixel by pixel
        # SETS self.dx or self.dy to appropriate values to not go through walls - it should be OK to run this over and over to get booleans
        if direction == "n":
            # Checking to the north. If dy > 0, then this could happen
            # bounds[y][x] returns True if that point is a collision
            if not globals.map.bounds[int((y + self.height) / globals.tile_h)][int(x / globals.tile_w)] == '=' and self.dy > 0:
                # only check for as far as they are trying to move
                if count < math.fabs(dy):
                    # it is not a collision and we have not checked the entire move yet
                    collision = self.dig(dx, dy, x, y + 1, count + 1, direction)    # recursify!  Increment y by one to check the pixel above this one
                else:
                    # it is not a collision and we have checked all possible collision points, so there is no collision
                    collision = False   # Ends recursion
            else:
                # it is a collision
                if self.dy > 0:
                    # they are trying to move in this direction
                    self.dy = count     # count at this point is equal to the number of pixels it checked before it came to a wall.  If it moves this much, it will be exactly next to the wall.
                    collision = True    # Ends recursion
                else:
                    # not trying to move this direction
                    collision = False   # no recursion happens
            return collision            # Give back result
        if direction == "s":
            if not globals.map.bounds[int(y / globals.tile_h)][int(x / globals.tile_w)] == '=' and self.dy < 0:
                if count < math.fabs(dy):
                    collision = self.dig(dx, dy, x, y - 1, count + 1, direction)
                else:
                    collision = False
            else:
                if self.dy < 0:
                    self.dy = -(math.fabs(count - 1))    # Since down is negative dy...
                    collision = True
                else:
                    collision = False
            return collision
        if direction == "se":
            if not globals.map.bounds[int(y / globals.tile_h)][int((x + self.width) / globals.tile_w)] == '=' and self.dx > 0:
                if count < math.fabs(dx):
                    collision = self.dig(dx, dy, x + 1, y, count + 1, direction)
                else:
                    collision = False
            else:
                if self.dx > 0:
                    self.dx = count
                    collision = True
                else:
                    collision = False
            return collision
        if direction == "sw":
            if not globals.map.bounds[int(y / globals.tile_h)][int(x / globals.tile_w)] == '=' and self.dx < 0:
                if count < math.fabs(dx):
                    collision = self.dig(dx, dy, x - 1, y, count + 1, direction)
                else:
                    collision = False
            else:				
                if self.dx < 0:
                    self.dx = -count
                    collision = True
                else:
                    collision = False
		return collision
        if direction == "ne":
            if not globals.map.bounds[int((y + self.height) / globals.tile_h)][int((x + self.width) / globals.tile_w)] == '=' and self.dx > 0:
                if count < math.fabs(dx):
                    collision = self.dig(dx, dy, x + 1, y, count + 1, direction)
                else:                    
                    collision = False
            else:
                if self.dx > 0:
                    self.dx = count     
                    collision = True            
                else:
                    collision = False
            return collision
        if direction == "nw":
            if not globals.map.bounds[int((y + self.height) / globals.tile_h)][int(x / globals.tile_w)] == '=' and self.dx < 0:
                if count < math.fabs(dx):
                    collision = self.dig(dx, dy, x - 1, y, count + 1, direction)
                else:
                    collision = False
            else:
                if self.dx < 0:
                    self.dx = -count
                    collision = True
                else:
                    collision = False
            return collision    
    def move(self):
        # actual drawing of the sprite will be handled elsewhere
        collision = self.isCollision()
        north = collision["north"]
        if north:
            pass
        if not (collision['north'] or collision['south']):
            self.y = self.y + self.dy
        if not (collision['east'] or collision['west']):
            self.x = self.x + self.dx           
# Used to access move states
class moves:
    def STATE_null(self, sprite):
        return spider_move.STATE_null(sprite)
    def STATE_idle(self, sprite):
        return spider_move.STATE_idle(sprite)
    def STATE_jump(self, sprite):
        return spider_move.STATE_jump(sprite) 
    def STATE_fall(self, sprite):
        return spider_move.STATE_fall(sprite)
# Used to access ai states
class ais:
    def STATE_null(self, sprite):
        return spider_ai.STATE_null(sprite)
# NULL is an initial state, goes to NEW
class STATE_null:
    "null"
    def __init__(self, sprite):
        self.spider = sprite    
    def update(self, dt):
        next_state = STATE_new(self.spider)
        return next_state
    def enter(self):
        print "enter spider.null"
    def leave(self):
        print "leave spider.null"

# IDLE runs while nothing else is going on in this FSM
class STATE_idle:
    "idle"
    def __init__(self, sprite):
        self.spider = sprite
    def update(self, dt):
        next_state = self
        if self.spider.hp <= 0:
            # since the spider has no more hp, go to death state
            next_state = STATE_death(self.spider)
        if self.spider.hp > 0:
            self.spider.ai_state.do_state(self.spider.ai_state.curr_state.update(dt))          # decides what to do
            self.spider.move_state.do_state(self.spider.move_state.curr_state.update(dt))      # calculates appropriate dx, dy            
            self.spider.move()                                                                 # applies dx, dy to x, y -- collision happens here always
        return next_state
    def enter(self):
        print "enter spider.idle"
    def leave(self):
        print "leave spider.idle"
    
# NEW initializes the spider object to default conditions
# goes to IDLE
class STATE_new:
    "new"
    def __init__(self, sprite):
        self.spider = sprite    
    def update(self, dt):
        next_state = STATE_idle(self.spider)
        self.spider.hp = self.spider.hp_max
        return next_state
    def enter(self):
        print "enter spider.new"
    def leave(self):
        print "leave spider.new"

# DEATH removes a life and cleans up spider object and maybe drops a powerup
class STATE_death:
    "death"
    def update(self, dt):
        return self
    def enter(self):
        print "enter spider.death"
    def leave(self):
        print "leave spider.death"
        
        