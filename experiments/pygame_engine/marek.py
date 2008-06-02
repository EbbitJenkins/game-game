import globals
import marek_move
import fsm      
import engine  
import pygame   # For extending Sprite
import math
import groups   # Sprite groups


# MAREK object will handle everything that marek does; it is instantiated in fsm as a global
# other sprite objects could be very similar to this
class marek(pygame.sprite.Sprite):
    def __init__(self, x, y, weight):
        pygame.sprite.Sprite.__init__(self)     # initialize pygame's sprite stuff        
        self.curr_state = STATE_null()          # initializes the state for the marek's FSM
        self.move_state = marek_move.move()     # initialize movement FSM
        self.moves = moves()                    # used to access list of move states
        self.images, self.rect = self.load_images()        # initialize images
        self.image = self.images['stand_right']  # Load image and rect
        groups.players.add(self)                            # Add sprite to player group
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
        images['stand_left'], rect = engine.loadImage('marek-left.png')
        images['stand_right'], rect = engine.loadImage('marek-right.png')
        return images, rect
		
    def update(self, dt):
        # runs the marek FSM
        self.do_state(self.curr_state.timer(dt))
    def do_keyboard(self, key, state):
        if state == pygame.KEYDOWN:
            if key == pygame.K_LEFT:
                if globals.debug:
                    print "PRESSED K_LEFT"
                self.dx = -self.run_speed
            elif key == pygame.K_RIGHT:
                if globals.debug:
                    print "PRESSED K_RIGHT"
                self.dx = self.run_speed
            elif key == pygame.K_SPACE:              
                if globals.debug:
                    print "PRESSED K_SPACE"
                if not self.move_state.curr_state.__doc__ == "jump":
                    if globals.debug:
                        print "Going to jump!"
                    self.move_state.action = self.moves.STATE_jump()
        elif state == pygame.KEYUP:
            if key == pygame.K_LEFT:
                if globals.debug:
                    print "UNPRESSED K_LEFT"
                self.dx = 0
            elif key == pygame.K_RIGHT:
                if globals.debug:
                    print "UNPRESSED K_RIGHT"            
                self.dx = 0
            elif key == pygame.K_SPACE:
                if globals.debug:
                    print "UNPRESSED K_SPACE"            
                self.move_state.action = self.moves.STATE_fall()            
    def do_state(self, next_state):
        if not (next_state == self.curr_state):
            self.curr_state.leave()
            
            self.curr_state = next_state
            
            self.curr_state.enter()
        return self.curr_state    
    # Uses rect to move by self.dx, self.dy
    def move(self):
        self.rect = self.rect.move(self.dx, self.dy)        
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
        if globals.player.hp == 0:
            # since the marek has no more hp, go to death state
            next_state = STATE_death()
        if globals.player.hp > 0:
            globals.player.move_state.do_state(globals.player.move_state.curr_state.timer(dt))    # calculates appropriate dx, dy
            globals.player.move()                                                                # applies dx, dy to x, y -- collision happens here always
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
        globals.player.hp = globals.player.hp_max
        globals.player.move_state.action = globals.player.moves.STATE_idle()
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
        globals.player.lives = globals.player.lives - 1
        print "LIVES REMAINING: %d" % (globals.player.lives, )
    def leave(self):
        print "leave marek.death"
        