import globals

# AI class holds a FSM that represents what sort of 'decision' state the sprite is in
# Based on these states and environmental factors, logic runs to decide which state to go to next
# These AI states directly influence the sprite's move states - most of their state transition logic is based on current AI state
# AI states calculate HOW to move and move states calculate WHERE to move
# Generally, collision detection is done in the AI states rather than the move states
# Of course, in this engine, there is a final collision check before any move is made anyway
class ai:
    # The AI FSM is initialized with a reference to the sprite it is controlling
    # Also, since the instances of the states will also need that reference, the initial curr_state is passed that same sprite
    def __init__(self, sprite):
        self.spider = sprite
        self.curr_state = STATE_null(self.spider)

    # do_state is called every cycle with curr_state.update(dt) as the parameter
    # curr_state.update(dt) will return which state the AI has decided it should go to next
    # Often, next_state will end up being the same state as before (curr_state.update returns self)
    # In the case of next_state not equal to curr_state, do_state leaves the curr_state and enters the next_state
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
        print "enter spider.ai.null"
    def leave(self):
		print "leave spider.ai.null"

# STATE_idle is for when the sprite is standing still.  It goes to either STATE_left or STATE_fall
# In this example, it is mainly used to decide if the spider will fall or not when it spawns
class STATE_idle:
    "idle"
    def __init__(self, sprite):
        self.spider = sprite     
    def update(self, dt):        
        next_state = self
        # isCollision returns a dictionary with results of collision checks in the cardinal directions
        collision = self.spider.isCollision()              
        # collision['south'] will be true if there is a wall within spider.dy pixels south of the sprite
        if collision['south']:
            # since it is on the ground, it should start walking left
            next_state = STATE_left(self.spider)                
        else:
            # since there is no wall below, it should be falling
            next_state = STATE_fall(self.spider)        
        return next_state
    def enter(self):
        print "enter spider.ai.idle"
    def leave(self):
        print "leave spider.ai.idle"

# STATE_left is for when the sprite is walking to the left.  It goes to either STATE_right, STATE_fall or STATE_jump
# In this example, the spider will walk to the left for spider.run_length seconds and then jump
# However, if it runs into a wall while walking left, it will switch to walking to the right
# Also, if it walks off of an edge, it should fall
# I am unsure how needed STATE_left and STATE_right are
# It may be more elegant to use STATE_idle for all 'basic' movement like walking and merely track which way it faces
# I already need to have a facing variable to determine which way to jump, but I suppose I will just see what problems this way causes
class STATE_left:
    "left"
    def __init__(self, sprite):
        self.spider = sprite     
    def update(self, dt):
        next_state = self
        collision = self.spider.isCollision()
        if not self.spider.isGrounded():
            next_state = STATE_fall(self.spider)
        elif collision['west']:
            next_state = STATE_right(self.spider)
        else:
            if self.timer < self.spider.run_length:            
                self.timer = self.timer + dt
            else:
                next_state = STATE_jump(self.spider)
        return next_state
    def enter(self):    
        print "enter spider.ai.left"
        self.timer = 0                  # adds dt to it every cycle
        self.spider.facing = 'west'     # used to determine which way it should jump
    def leave(self):
        print "leave spider.ai.left"

# STATE_right is for when the sprite is walking to the right.  It goes to either STATE_right or STATE_jump
# See description of STATE_left, same thing
class STATE_right:
    "right"
    def __init__(self, sprite):
        self.spider = sprite     
    def update(self, dt):
        next_state = self
        collision = self.spider.isCollision()        
        if not self.spider.isGrounded():
            next_state = STATE_fall(self.spider)        
        elif collision["east"]:
            next_state = STATE_left(self.spider)
        else:
            if self.timer <= self.spider.run_length:            
                self.timer = self.timer + dt
            if self.timer >= self.spider.run_length:
                next_state = STATE_jump(self.spider)
        return next_state
    def enter(self):    
        print "enter spider.ai.right"
        self.timer = 0    
        self.spider.facing = 'east'
    def leave(self):
        print "leave spider.ai.right"
        
# STATE_jump is for when the sprite is ascending in a jump.  It goes to STATE_fall
# In this example, the spider jumps for spider.jump_height seconds
# Once it has jumped all that it can, it goes to STATE_fall
class STATE_jump:
    "jump"
    def __init__(self, sprite):
        self.spider = sprite
    def update(self, dt):
        next_state = self           
        if self.timer <= self.spider.jump_height:
            self.timer = self.timer + dt
        else:
            next_state = STATE_fall(self.spider)
        return next_state
    def enter(self):
        print "enter spider.ai.jump"
        self.timer = 0
    def leave(self):
        print "leave spider.ai.jump"

# STATE_fall is for when the sprite is falling, for whatever reason.  It goes to either STATE_right or STATE_left
# When it sees a collision to the south, it then check which direction it is facing and moves to the appropriate state
class STATE_fall:
    "fall"
    def __init__(self, sprite):
        self.spider = sprite
    def update(self, dt):
        next_state = self
        collision = self.spider.isCollision()     
        if collision['south']:     
            if self.spider.facing == 'east':
                next_state = STATE_right(self.spider)
            else:
                next_state = STATE_left(self.spider)
        return next_state
    def enter(self):
        print "enter spider.ai.fall"
    def leave(self):
        print "leave spider.ai.fall"