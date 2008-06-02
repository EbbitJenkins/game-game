import globals
import marek_move
import fsm
import engine
import math


# MAREK object will handle everything that marek does; it is instantiated in fsm as a global
# other sprite objects could be very similar to this
class marek:
    def __init__(self, x, y, weight):
        self.curr_state = STATE_null()    # initializes the state for the marek's FSM
        self.move_state = marek_move.move()
        self.moves = moves()    # used to access list of move states
        self.images = self.load_images()
        self.image = self.images['stand_right']
        self.width, self.height = self.image.width, self.image.height
        self.buffer = 5         # used for collision
        self.active = False 	# is in camera?
        self.hp = 100           # marek's current hp
        self.hp_max = 100       # max hp marek currently can have
        self.lives = 3          # times that marek can die
        self.dx = 0             # directional x-vector, max 1, min -1
        self.dy = 0             # directional y-vector, max 1, min -1
        self.x = x              # position on x-axis
        self.y = y              # position on y-axis
        self.weight = weight	# how fast marek falls
        self.run_speed = 5      # how fast marek runs
        self.jump_speed = self.weight * 3  # how fast marek ascends/descends when he jumps or falls
        self.jump_height = 1    # how long marek can jump for, in seconds
        self.jump_arc = 3       # how fast marek can move in x-axis while jumping or falling

    def load_images(self):
        images = {}
        images['stand_left'] = engine.load_image('marek-left.png')
        images['stand_right'] = engine.load_image('marek-right.png')
        return images
		
    def do_timer(self, dt):
        # runs the marek FSM - no return is necissary since do_state has access to self.curr_state
        self.do_state(self.curr_state.timer(dt))
        
    def do_state(self, next_state):
        if not (next_state == self.curr_state):
            self.curr_state.leave()
            
            self.curr_state = next_state
            
            self.curr_state.enter()
        return self.curr_state

    def isCollision(self):
        # Computes boolean values for each of the 6 adjacent tiles
		# Returns whether or not marek can move in the directions specified in self.dx, self.dy

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
        
        isCollided = False       

        # If the sprite is bound in the direction it is going, return false
        if (dx > 0 and bound_e) or (dx < 0 and bound_w) or (dy > 0 and bound_n) or (dy < 0 and bound_s): 
            #print "Collision detected! dx: " + str(dx) + ", dy: " + str(dy) + ", x: " + str(self.x) + ", y: " + str(self.y)
            isCollided = True                    
        
        return isCollided
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
            print "Recursion level " + str(count)
            if not globals.map.bounds[int(y / globals.tile_h)][int(x / globals.tile_w)] == '=' and self.dy < 0:
                print "No collision, x, y: " + str(x) + ", " + str(y)
                if count < math.fabs(dy):
                    print "Deeper..."
                    collision = self.dig(dx, dy, x, y - 1, count + 1, direction)
                else:
                    print "Recurstion ending, no collision found"
                    collision = False
            else:
                print "Collision or not moving"
                if self.dy < 0:
                    print "Recurstion ending, collision detected, self.dy = " + str(-count)
                    self.dy = -(math.fabs(count - 1))    # Since down is negative dy...
                    collision = True
                else:
                    print "No collision"
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
    def do_collision(self, dx, dy):
		# Computes boolean values for each of the 6 adjacent tiles
		# Returns whether or not marek can move in the directions specified with dx, dy

        # Since this sprite is 1x2 tiles, we need 4 x bounds
        #    n
        # nw P ne
        # sw P se
        #    s

        w, h = globals.tile_w, globals.tile_h
        x, y = math.ceil(self.x), math.ceil(self.y)

        bound_n  = globals.map.bounds[int((y + self.height + self.buffer) / h)][int(x / w)] == '='
        bound_s  = globals.map.bounds[int((y - self.buffer) / h)][int(x / w)] == '='
        bound_se = globals.map.bounds[int(y / h)][int((x + self.width + self.buffer) / w)] == '='
        bound_sw = globals.map.bounds[int(y / h)][int((x - self.buffer) / w)] == '='
        bound_ne = globals.map.bounds[int((y + h + self.buffer)/h)][int((x + self.buffer + self.width)/w)] == '='
        bound_nw = globals.map.bounds[int((y + h + self.buffer) / h)][int((x - self.buffer) / w)] == '='

        # Might as well combine x directions
        bound_e = bound_se or bound_ne
        bound_w = bound_nw or bound_sw

        # If the sprite is bound in the direction it is going, return false
        if (dx > 0 and bound_e) or (dx < 0 and bound_w): 
            print "Collision detected! dx: " + str(dx)
            dx = 0        
        if (dy > 0 and bound_n) or (dy < 0 and bound_s):
            #print "dy: " + str(dy)
            dy = 0
        
        return dx, dy
    def gravity(self, dt):
        self.move(0, -self.weight, dt)
    def move(self):
        # actual drawing of the sprite will be handled elsewhere
        #dx, dy = self.do_collision(dx, dy)
        if not self.isCollision():
            self.x = self.x + self.dx
            self.y = self.y + self.dy
    
# Used to access move states
class moves:
    def STATE_null(self):
        return marek_move.STATE_null()
    def STATE_idle(self):
        return marek_move.STATE_idle()
    def STATE_jump(self):
        return marek_move.STATE_jump() 
    def STATE_fall(self):
        return marek_move.STATE_fall()
# NULL is an initial state, goes to NEW
class STATE_null:
    "null"
    def timer(self, dt):
        next_state = STATE_new()
        return next_state
    def enter(self):
        print "enter marek.null"
    def leave(self):
        print "leave marek.null"

# IDLE runs while nothing else is going on in this FSM
# In theory, there will be 3-4 more FSM being run from within idle.timer, controlling movement, attacks, collision and (in the case of NPC) AI
class STATE_idle:
    "idle"
    def timer(self, dt):
        next_state = self
        if globals.marek.hp == 0:
            # since the marek has no more hp, go to death state
            next_state = STATE_death()
        if globals.marek.hp > 0:
            globals.marek.move_state.do_state(globals.marek.move_state.curr_state.timer(dt))    # calculates appropriate dx, dy
            globals.marek.move()                                                                # applies dx, dy to x, y -- collision happens here always
        return next_state
    def enter(self):
        print "enter marek.idle"
    def leave(self):
        print "leave marek.idle"
    
# NEW initializes the marek object to default conditions, such as when you come back from death
# goes to IDLE
class STATE_new:
    "new"
    def timer(self, dt):
        next_state = STATE_idle()
        globals.marek.hp = globals.marek.hp_max
        globals.marek.move_state.action = globals.marek.moves.STATE_idle()
        return next_state
    def enter(self):
        print "enter marek.new"
    def leave(self):
        print "leave marek.new"

# DEATH removes a life and goes back to NEW
class STATE_death:
    "death"
    def timer(self, dt):
        next_state = STATE_new()
        return next_state
    def enter(self):
        print "enter marek.death"
        globals.marek.lives = globals.marek.lives - 1
        print "LIVES REMAINING: %d" % (globals.marek.lives, )
    def leave(self):
        print "leave marek.death"
        