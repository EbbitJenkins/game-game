import globals

# Move class holds a FSM that represents what sort of movement state the sprite is in
# Depending on the state, different types of formula will be used to calculate the sprite's dx and dy
# The logic to determine which state to go to next is determined by the current state of the AI FSM
# AI states calculate HOW to move and move states calculate WHERE to move
# There is no collision checks in move states - they caluclate where it wants to move
# After the move has been calculated, but before the actual position of the sprite is changed, 
# a final pass of collision checking happens that corrects the dx and dy to not go through walls
class move:
    # See spider_ai.py for equivalent descriptions
    def __init__(self, sprite):
        self.spider = sprite
        self.curr_state = STATE_null(self.spider)

    def do_state(self, next_state):
        if not (next_state == self.curr_state):
            self.curr_state.leave()
            
            self.curr_state = next_state
            
            self.curr_state.enter()
        return self.curr_state
		
# STATE_null serves as the entry point into the FSM, it goes to STATE_idle
class STATE_null:
    "null"
    def __init__(self, sprite):
        self.spider = sprite     
    def update(self, dt):
        return STATE_idle(self.spider)
    def enter(self):
        print "enter spider.move.null"
    def leave(self):
		print "leave spider.move.null"
# STATE_idle is for 'general' movement, like walking back and forth.  It goes to either STATE_jump or STATE_fall
# The update method is mostly a switch statement.  Didn't seem like python had a switch statement in the api.
# Depending on the curr_state of the AI FSM, idle does the appropriate stuff
class STATE_idle:
    "idle"
    def __init__(self, sprite):
        self.spider = sprite  
    def update(self, dt):
        next_state = self       
        # AI in STATE_idle means spider is still, no state change
        if self.spider.ai_state.curr_state.__doc__ == "idle":
            self.spider.dx = 0
            self.spider.dy = 0
        # AI in STATE_jump means next_state will be STATE_jump
        if self.spider.ai_state.curr_state.__doc__ == "jump":
            next_state = STATE_jump(self.spider)
        # AI in STATE_fall means next_state will be STATE_fall
        if self.spider.ai_state.curr_state.__doc__ == "fall":
            next_state = STATE_fall(self.spider)
        # AI in STATE_left means spider moves to the left, no state change
        if self.spider.ai_state.curr_state.__doc__ == "left":                   
            self.spider.dx = -self.spider.run_speed
            self.spider.dy = 0
            self.spider.image = self.spider.images['stand_left']    # animation would run here, or perhaps in its own, higher-level FSM
        # AI in STATE_right means spider moves to the right, no state change
        if self.spider.ai_state.curr_state.__doc__ == "right":
            self.spider.dx = self.spider.run_speed
            self.spider.dy = 0
            self.spider.image = self.spider.images['stand_right']
        return next_state        
    def enter(self):
        print "enter spider.move.idle"
    def leave(self):
		print "leave spider.move.idle"
# STATE_fall is for when the sprite is falling, for whatever reason.  It goes to STATE_idle
# In this example, it goes to STATE_idle when the AI state is no longer STATE_fall
# STATE_fall can be reached by either STATE_jump or STATE_idle
# The dy when this state is entered is assumed to be either 0 or close to 0
# I don't specifically set it to 0 during entry so that the jump curve will be smoother
class STATE_fall:
    "fall"
    def __init__(self, sprite):
        self.spider = sprite 
    def update(self, dt):
        next_state = self      
        self.timer = self.timer + dt
        if self.spider.ai_state.curr_state.__doc__ == "fall":
            # This is designed so that the sprite accelerates down at 3 points during the fall,
            # until it reaches it's max speed of jump_speed, which is a function of the sprite's weight
            if self.timer >= self.spider.jump_height/3.0:                
                self.timer = 0
                if self.spider.dy > -self.spider.jump_speed:
                    self.spider.dy = self.spider.dy - self.spider.jump_speed/3.0
        else:
            next_state = STATE_idle(self.spider)
        return next_state
    def enter(self):
        print "enter spider.move.fall"
        self.timer = self.spider.jump_height/3.0  # Controls acceleration
    def leave(self):
        print "leave spider.move.fall"
# STATE_jump is for when the sprite is ascending in a jump.  It goes to STATE_fall
# When entered, it sets dy to jump_speed and the ascent slows as the jump progresses
class STATE_jump:
    "jump"
    def __init__(self, sprite):
        self.spider = sprite     
    def update(self, dt):
        next_state = self
        self.timer = self.timer + dt
        if self.spider.ai_state.curr_state.__doc__ == "jump":
            # See STATE_fall
            if self.timer >= self.spider.jump_height/3.0:
                self.timer = 0
                # gets slower as it goes up
                if self.spider.dy > 0:
                    self.spider.dy = self.spider.dy - self.spider.jump_speed/3.0
        else:
            next_state = STATE_fall(self.spider)
        return next_state
    def enter(self):
        print "enter spider.move.jump"        
        self.timer = self.spider.jump_height/3.0    #used to control how quickly ascent slows        
        self.spider.dy = self.spider.jump_speed     # initialize dy
        if self.spider.facing == 'east':            # determine which direction to jump
            self.spider.dx = self.spider.jump_arc        
        else:
            self.spider.dx = -self.spider.jump_arc
    def leave(self):
        print "leave spider.move.jump"
        