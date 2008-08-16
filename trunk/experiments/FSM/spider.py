import math

import globals
import sprite
import fsm
import em
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
        self.curr_state = STATE_new(self)
        self.ai_FSM = fsm.FSM(spider_ai.STATE_null(self))       # initializes spider AI FSM
        self.em = em.EventMachine(self)                         #  handles events        
        self.hp = 100                           # spider's current hp
        self.hp_max = 100                       # max hp spider currently can have
        self.weight = 2     	                # how fast spider falls
        self.run_x = 1                          # how many x-pixels the spider will move each frame, while walking
        self.run_y = 0                          # how many y-pixels the spider will move each frame, while walking
        self.run_length = 100                   # how long spider walks in each direction, in frames
        self.jump_y = self.weight * 3.0         # how fast spider ascends/descends when he jumps or falls, in y-pixels
        self.jump_x = 3                         # how many x-pixels the spider will move while jumping
        self.jump_height = 10                   # how long spider can jump for, in frames
        self.bullet_speed = 4                   # how fast bullets go
        self.gravity = 'south'                  # which direction is falling (unused)
        self.facing = 'west'                    # which direction it is facing

     

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
            self._sprite.ai_FSM.do_state(self._sprite.ai_FSM.curr_state.update())           # decides what to do, issues events
            self._sprite.em.update()                                                        #  handles events
            self._sprite.move()                                                             # applies d['x'], d['y'] to x, y -- collision happens here always
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
        
        