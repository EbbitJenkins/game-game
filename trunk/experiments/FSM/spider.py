import math

import globals
import sprite
import fsm
import engine

import spider_ai
import spider_move


# SPIDER
# A mechanical spider than hops around and can attach to walls and
# ceilings. It's annoying enough not to require its own weapon, and it's
# lightly armored so one shot kills it. It moves at a comparable speed
# to Marek walking.
#
# Note: that is the plan, not the reality at this point
# ----------------------------------------------------------------------------------------
class spider(sprite.Sprite):
    # creates all of the attributes describing the sprite's behavior
    def _init(self):
        self.curr_state = STATE_null(self)
        self.move_FSM = fsm.FSM(spider_move.STATE_null(self))   # initializes spider movement FSM
        self.ai_FSM = fsm.FSM(spider_ai.STATE_null(self))       # initializes spider AI FSM
        self.image = self.images['stand_right']               # spider initial graphic
        self._width = self.image.width          # spider's width
        self._height = self.image.height        # spider's height
        self.hp = 100                           # spider's current hp
        self.hp_max = 100                       # max hp spider currently can have
        self.weight = 2     	                # how fast spider falls
        self.run_speed = 2                      # how fast spider runs
        self.run_length = 1                     # how long spider walks in each direction
        self.jump_speed = self.weight * 3.0     # how fast spider ascends/descends when he jumps or falls
        self.jump_height = 2                    # how long spider can jump for, in seconds
        self.jump_arc = 3                       # how fast spider can move in x-axis while jumping or falling
        self.gravity = 'south'                  # which direction is falling
        self.facing = 'west'                    # which direction it is facing

    def _load_images(self):
        images = {}
        images['stand_left'] = engine.load_image('spider.png')
        images['stand_right'] = engine.load_image('spider.png')
        return images        

class STATE_null(sprite.SpriteState):
    def __init__(self, sprite):
        self._name = "null"
        self._sprite = sprite
    def update(self, dt):
        next_state = STATE_new(self._sprite)
        return next_state
    def enter(self):
        print "enter spider.null"
    def leave(self):
        print "leave spider.null"

# IDLE runs while nothing else is going on in this FSM
class STATE_idle(sprite.SpriteState):
    def __init__(self, sprite):
        self._name = "idle"        
        self._sprite = sprite
    def update(self, dt):
        next_state = self
        if self._sprite.hp <= 0:
            # since the spider has no more hp, go to death state
            next_state = STATE_death(self._sprite)
        if self._sprite.hp > 0:
            self._sprite.ai_FSM.do_state(self._sprite.ai_FSM.curr_state.update(dt))          # decides what to do
            self._sprite.move_FSM.do_state(self._sprite.move_FSM.curr_state.update(dt))      # calculates appropriate d['x'], d['y']   
            self._sprite.move()                                                              # applies d['x'], d['y'] to x, y -- collision happens here always
        return next_state
    def enter(self):
        print "enter spider.idle"
    def leave(self):
        print "leave spider.idle"
    
# NEW initializes the spider object to default conditions
# goes to IDLE
class STATE_new(sprite.SpriteState):
    def __init__(self, sprite):
        self._name = "new"
        self._sprite = sprite    
    def update(self, dt):
        next_state = STATE_idle(self._sprite)
        self._sprite.hp = self._sprite.hp_max
        return next_state
    def enter(self):
        print "enter spider.new"
    def leave(self):
        print "leave spider.new"

# DEATH removes a life and cleans up spider object and maybe drops a powerup
class STATE_death(sprite.SpriteState):
    def __init__(self, sprite):
        self._name = "death"        
        self._sprite = sprite
    def update(self, dt):
        return self
    def enter(self):
        print "enter spider.death"
    def leave(self):
        print "leave spider.death"
        
        