import globals
import sprite
import fsm
import em
import engine

class Bullet(sprite.Sprite):
    def _init(self, dx, dy):
        self.curr_state = STATE_new(self)
        self.em = em.EventMachine(self)                         
        self.hp = 1
        self.d['x'] = dx
        self.d['y'] = dy
   
class STATE_new(sprite.SpriteState):    
    def __init__(self, sprite):
        self._name = "new"
        self._sprite = sprite                  
            
    def update(self, dt):
        next_state = STATE_idle(self._sprite)        
        return next_state
    def enter(self):
        print "enter bullet.new"
    def leave(self):
        print "leave bullet.new"
        
class STATE_idle(sprite.SpriteState):
    def __init__(self, sprite):
        self._name = "idle"        
        self._sprite = sprite
                
        @sprite.em.event
        def onWalk(event, sprite):        
            pass
    def update(self, dt):
        next_state = self
        collision = self._sprite.isCollision()
        if collision['west'] or collision['east']:
            next_state = STATE_death(self._sprite)
        else:          
            self._sprite.em.update()                                                        
            self._sprite.move()                                                            
        return next_state
    def enter(self):
        print "enter bullet.idle"
        self._sprite.em.notify("onWalk", "start")
    def leave(self):
        print "leave bullet.idle"
        self._sprite.em.notify("onWalk", "end")
        
class STATE_death(sprite.SpriteState):
    def __init__(self, sprite):
        self._name = "death"        
        self._sprite = sprite
        
        @sprite.em.event
        def onCollide(event, sprite):            
            sprite.em.notify("onCollide", "end")
            globals.bullets.remove(sprite)
    def update(self, dt):  
        self._sprite.em.update()    
        return self
    def enter(self):
        print "enter bullet.death"
        self._sprite.em.notify("onCollide", "start")
    def leave(self):
        print "leave bullet.death"