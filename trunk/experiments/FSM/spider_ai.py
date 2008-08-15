import sprite

# These states are used by the spider.ai_FSM as possible states
# Based on these states and environmental factors, logic runs to decide which state to go to next
# These AI states directly influence the sprite's move states - most of their state transition logic is based on current AI state
# AI states calculate HOW to move and move states calculate WHERE to move
# Generally, collision detection is done in the AI states rather than the move states
# Of course, in this engine, there is a final collision check before any move is made anyway

# STATE_null serves as the entry point into the FSM, it goes to STATE_idle
class STATE_null(sprite.SpriteState):
    def __init__(self, sprite):
        self._name = "null"
        self._sprite = sprite     
    def update(self):
        return STATE_idle(self._sprite)
    def enter(self):
        print "enter spider.ai.null"
    def leave(self):
		print "leave spider.ai.null"

# STATE_idle is for when the sprite is standing still.  It goes to either STATE_left or STATE_fall
# In this example, it is mainly used to decide if the spider will fall or not when it spawns
class STATE_idle(sprite.SpriteState):
    def __init__(self, sprite):
        self._name = "idle"
        self._sprite = sprite     
        
        # EVENTS
        @self._sprite.em.event
        def onIdle(event, sprite):
            sprite.d['x'] = 0        
    def update(self):        
        next_state = self
        # isCollision returns a dictionary with results of collision checks in the cardinal directions
        collision = self._sprite.isCollision()              
        # collision['south'] will be true if there is a wall within spider.d['y'] pixels south of the sprite
        if collision['south']:
            # since it is on the ground, it should start walking left
            next_state = STATE_left(self._sprite)                
        else:
            # since there is no wall below, it should be falling
            next_state = STATE_fall(self._sprite)        
        return next_state
    def enter(self):
        print "enter spider.ai.idle"
        self._sprite.em.notify("onIdle", "start")
    def leave(self):
        print "leave spider.ai.idle"
        self._sprite.em.notify("onIdle", "end")       

# STATE_left is for when the sprite is walking to the left.  It goes to either STATE_right, STATE_fall or STATE_jump
# In this example, the spider will walk to the left for spider.run_length seconds and then jump
# However, if it runs into a wall while walking left, it will switch to walking to the right
# Also, if it walks off of an edge, it should fall
# I am unsure how needed STATE_left and STATE_right are
# It may be more elegant to use STATE_idle for all 'basic' movement like walking and merely track which way it faces
# I already need to have a facing variable to determine which way to jump, but I suppose I will just see what problems this way causes
class STATE_left(sprite.SpriteState):
    def __init__(self, sprite):
        self._name = "left"
        self._sprite = sprite     
        
        # EVENTS
        @self._sprite.em.event
        def onWalkLeft(self, sprite):
            sprite.d['x'] = -sprite.run_speed
    def update(self):
        next_state = self
        collision = self._sprite.isCollision()
        if not self._sprite.isGrounded():
            next_state = STATE_fall(self._sprite)
        elif collision['west']:
            next_state = STATE_right(self._sprite)
        else:
            if self._timer < self._sprite.run_length:            
                self._timer = self._timer + 1
            else:
                next_state = STATE_jump(self._sprite)
        return next_state
    def enter(self):    
        print "enter spider.ai.left"
        self._sprite.em.notify("onWalkLeft", "start")        
        self._timer = 0                  # adds dt to it every cycle
        self._sprite.facing = 'west'     # used to determine which way it should jump
    def leave(self):        
        print "leave spider.ai.left"
        self._sprite.em.notify("onWalkLeft", "end")       
        

# STATE_right is for when the sprite is walking to the right.  It goes to either STATE_right or STATE_jump
# See description of STATE_left, same thing
class STATE_right(sprite.SpriteState):
    def __init__(self, sprite):
        self._name = "right"
        self._sprite = sprite     
        
        #  EVENTS
        @self._sprite.em.event
        def onWalkRight(event, sprite):
            sprite.d['x'] = sprite.run_speed            
    def update(self):
        next_state = self
        collision = self._sprite.isCollision()        
        if not self._sprite.isGrounded():
            next_state = STATE_fall(self._sprite)        
        elif collision["east"]:
            next_state = STATE_left(self._sprite)
        else:
            if self._timer <= self._sprite.run_length:            
                self._timer = self._timer + 1
            if self._timer >= self._sprite.run_length:
                next_state = STATE_jump(self._sprite)
        return next_state
    def enter(self):    
        print "enter spider.ai.right"
        self._sprite.em.notify("onWalkRight", "start")        
        self._timer = 0    
        self._sprite.facing = 'east'
    def leave(self):
        print "leave spider.ai.right"
        self._sprite.em.notify("onWalkRight", "end")
        
            
# STATE_jump is for when the sprite is ascending in a jump.  It goes to STATE_fall
# In this example, the spider jumps for spider.jump_height seconds
# Once it has jumped all that it can, it goes to STATE_fall
class STATE_jump(sprite.SpriteState):
    def __init__(self, sprite):
        self._name = "jump"
        self._sprite = sprite
        
        #  EVENTS
        @self._sprite.em.event
        def onJump(event, sprite):
            if event._frame == 0:
                sprite.d['y'] = 0
            if event._timer > sprite.jump_height/5:
                event.reset_timer()
                sprite.d['y'] = sprite.d['y'] + sprite.jump_speed/5
    def update(self):
        next_state = self          
        self._timer = self._timer + 1
        if self._timer >= self._sprite.jump_height:           
            next_state = STATE_fall(self._sprite)
        return next_state
    def enter(self):
        print "enter spider.ai.jump"
        self._timer = 0
        self._sprite.em.notify("onJump", "start")
    def leave(self):
        print "leave spider.ai.jump"
        self._sprite.em.notify("onJump", "end")
    

# STATE_fall is for when the sprite is falling, for whatever reason.  It goes to either STATE_right or STATE_left
# When it sees a collision to the south, it then check which direction it is facing and moves to the appropriate state
class STATE_fall(sprite.SpriteState):
    def __init__(self, sprite):
        self._name = "fall"
        self._sprite = sprite
        
        #  EVENTS             
        @self._sprite.em.event
        def onFall(event, sprite):
            if event._frame == 0:
                sprite.d['y'] = 0
            print "-timer: " + str(event._timer) + " frame: " + str(event._frame) + " - jump_height/5: " + str(sprite.jump_height/5.0)
            if event._timer > sprite.jump_height/5:
                event.reset_timer()
                sprite.d['y'] = sprite.d['y'] - sprite.jump_speed/5     
    def update(self):
        next_state = self
        collision = self._sprite.isCollision()     
        if collision['south']:     
            if self._sprite.facing == 'east':
                next_state = STATE_right(self._sprite)
            else:
                next_state = STATE_left(self._sprite)
        return next_state
    def enter(self):
        print "enter spider.ai.fall"
        self._sprite.em.notify("onFall", "start")
    def leave(self):
        print "leave spider.ai.fall"
        self._sprite.em.notify("onFall", "end")
            