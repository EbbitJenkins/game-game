import globals
import marek_move
import fsm
import engine


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
        self.active = False 	# is in camera?
        self.hp = 100           # marek's current hp
        self.hp_max = 100       # max hp marek currently can have
        self.lives = 3          # times that marek can die
        self.dx = 0             # directional x-vector, max 1, min -1
        self.dy = 0             # directional y-vector, max 1, min -1
        self.x = x              # position on x-axis
        self.y = y              # position on y-axis
        self.weight = weight	# how fast marek falls
        self.run_speed = 2      # how fast marek runs
        self.jump_speed = self.weight + 3  #how fast marek jumps
        self.jump_height = 1    # how long marek can jump for, in seconds

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

    def isCollision(self, dx, dy):
		# Computes boolean values for each of the 6 adjacent tiles
		# Returns whether or not marek can move in the directions specified with dx, dy

        # Since this sprite is 1x2 tiles, we need 4 x bounds
        #    n
        # nw P ne
        # sw P se
        #    s

        w, h = globals.tile_w, globals.tile_h

        bound_n  = globals.map.bounds[(self.y + self.height + 1) / h][self.x / w] == '='
        bound_s  = globals.map.bounds[(self.y - 1) / h][self.x / w] == '='
        bound_se = globals.map.bounds[self.y / h][(self.x + self.width + 1) / w] == '='
        bound_sw = globals.map.bounds[self.y / h][(self.x - 1) / w] == '='
        bound_ne = globals.map.bounds[(self.y + h+1)/h][(self.x + 1 + self.width)/w] == '='
        bound_nw = globals.map.bounds[(self.y + h + 1) / h][(self.x - 1) / w] == '='

        # Might as well combine x directions
        bound_e = bound_se or bound_ne
        bound_w = bound_nw or bound_sw
		
        isCollided = False

        # If the sprite is bound in the direction it is going, return false
        if (dx > 0 and bound_e) or (dx < 0 and bound_w) or (dy > 0 and bound_n) or (dy < 0 and bound_s):
            isCollided = True
        
        return isCollided
    def gravity(self):
        self.move(0, -self.weight)
    def move(self, dx, dy):
        # actual drawing of the sprite will be handled elsewhere
		if not self.isCollision(dx, dy):
			self.x = self.x + dx
			self.y = self.y + dy
    
# Used to access move states
class moves:
    def STATE_null(self):
        return marek_move.STATE_null()
    def STATE_idle(self):
        return marek_move.STATE_idle()
    def STATE_jump(self):
        return marek_move.STATE_jump()    
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
            globals.marek.move_state.do_state(globals.marek.move_state.curr_state.timer(dt))
            globals.marek.gravity()
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
        