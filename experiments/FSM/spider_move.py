import sprite

# These states are used in the spider.move_FSM as possible states
# Depending on the state, different types of formula will be used to calculate the sprite's d['x'] and d['y']
# The logic to determine which state to go to next is determined by the current state of the AI FSM
# AI states calculate HOW to move and move states calculate WHERE to move
# There is no collision checks in move states - they caluclate where it wants to move
# After the move has been calculated, but before the actual position of the sprite is changed, 
# a final pass of collision checking happens that corrects the d['x'] and d['y'] to not go through walls

# STATE_null serves as the entry point into the FSM, it goes to STATE_idle
class STATE_null(sprite.SpriteState):
    def __init__(self, sprite):
        self._name = "null"
        self._sprite = sprite     
    def update(self, dt):
        return STATE_idle(self._sprite)
    def enter(self):
        print "enter spider.move.null"
    def leave(self):
		print "leave spider.move.null"
# STATE_idle is for 'general' movement, like walking back and forth.  It goes to either STATE_jump or STATE_fall
# The update method is mostly a switch statement.  Didn't seem like python had a switch statement in the api.
# Depending on the curr_state of the AI FSM, idle does the appropriate stuff
class STATE_idle(sprite.SpriteState):
    def __init__(self, sprite):
        self._name = "idle"
        self._sprite = sprite  
    def update(self, dt):
        next_state = self       
        # AI in STATE_idle means spider is still, no state change
        if str(self._sprite.ai_FSM.curr_state) == "idle":
            self._sprite.d['x'] = 0
            self._sprite.d['y'] = 0
        # AI in STATE_jump means next_state will be STATE_jump
        if str(self._sprite.ai_FSM.curr_state) == "jump":
            next_state = STATE_jump(self._sprite)
        # AI in STATE_fall means next_state will be STATE_fall
        if str(self._sprite.ai_FSM.curr_state) == "fall":
            next_state = STATE_fall(self._sprite)
        # AI in STATE_left means spider moves to the left, no state change
        if str(self._sprite.ai_FSM.curr_state) == "left":                   
            self._sprite.d['x'] = -self._sprite.run_speed
            self._sprite.d['y'] = 0
            self._sprite.image = self._sprite.images['stand_left']    # animation would run here, or perhaps in its own, higher-level FSM
        # AI in STATE_right means spider moves to the right, no state change
        if str(self._sprite.ai_FSM.curr_state) == "right":
            self._sprite.d['x'] = self._sprite.run_speed
            self._sprite.d['y'] = 0
            self._sprite.image = self._sprite.images['stand_right']
        return next_state        
    def enter(self):
        print "enter spider.move.idle"
    def leave(self):
		print "leave spider.move.idle"
# STATE_fall is for when the sprite is falling, for whatever reason.  It goes to STATE_idle
# In this example, it goes to STATE_idle when the AI state is no longer STATE_fall
# STATE_fall can be reached by either STATE_jump or STATE_idle
# The d['y'] when this state is entered is assumed to be either 0 or close to 0
# I don't specifically set it to 0 during entry so that the jump curve will be smoother
class STATE_fall(sprite.SpriteState):
    def __init__(self, sprite):
        self._name = "fall"
        self._sprite = sprite 
    def update(self, dt):
        next_state = self      
        self._timer = self._timer + dt        
        if str(self._sprite.ai_FSM.curr_state) == "fall":
            # This is designed so that the sprite accelerates down at 3 points during the fall,
            # until it reaches it's max speed of jump_speed, which is a function of the sprite's weight
            if self._timer >= self._sprite.jump_height/3.0:                
                self._timer = 0
                if self._sprite.d['y'] > -self._sprite.jump_speed:
                    self._sprite.d['y'] = self._sprite.d['y'] - self._sprite.jump_speed/3.0
        else:
            next_state = STATE_idle(self._sprite)
        return next_state
    def enter(self):
        print "enter spider.move.fall"
        self._timer = self._sprite.jump_height/3.0  # Controls acceleration
    def leave(self):
        print "leave spider.move.fall"
# STATE_jump is for when the sprite is ascending in a jump.  It goes to STATE_fall
# When entered, it sets d['y'] to jump_speed and the ascent slows as the jump progresses
class STATE_jump(sprite.SpriteState):
    def __init__(self, sprite):
        self._name = "jump"
        self._sprite = sprite     
    def update(self, dt):
        next_state = self
        self._timer = self._timer + dt
        if str(self._sprite.ai_FSM.curr_state) == "jump":
            # See STATE_fall
            if self._timer >= self._sprite.jump_height/3.0:
                self._timer = 0
                # gets slower as it goes up
                if self._sprite.d['y'] > 0:
                    self._sprite.d['y'] = self._sprite.d['y'] - self._sprite.jump_speed/3.0
        else:
            next_state = STATE_fall(self._sprite)
        return next_state
    def enter(self):
        print "enter spider.move.jump"        
        self._timer = self._sprite.jump_height/3.0      #used to control how quickly ascent slows        
        self._sprite.d['y'] = self._sprite.jump_speed   # initialize d['y']
        if self._sprite.facing == 'east':               # determine which direction to jump
            self._sprite.d['x'] = self._sprite.jump_arc        
        else:
            self._sprite.d['x'] = -self._sprite.jump_arc
    def leave(self):
        print "leave spider.move.jump"
        