import globals
import engine
import state
import marek
import spider
import em

#LOAD state is for loading a map, as well as everything involved with the map.  Goes to PLAY
class STATE_load(state.State):
    def update(self, dt):
        next_state = engine.STATE_play()
        self.init()  #initialize stuffs!
        return next_state
    def enter(self):
        print "enter load"
    def leave(self):
        print "leave load"
    def init(self):	    
        #  This should all be done by the manifest parser
        globals.marek = marek.marek(120, 100, 2)    # initialize the marek object        
        increment = 580/int(globals.spider_number)
        for i in range(20, 600, increment):            
            sprite = spider.spider(i, 420)          
            images = [engine.load_image('spider.png')]
            ani = em.Animation(images)            
            event = em.SpriteEvent("onIdle", None, ani, 0, 0)
            sprite.em.add(event)
            event = em.SpriteEvent("onWalkLeft", None, ani, 0, 0)
            sprite.em.add(event)
            event = em.SpriteEvent("onWalkRight", None, ani, 0, 0)
            sprite.em.add(event)
            event = em.SpriteEvent("onJump", None, ani, 0, 0)
            sprite.em.add(event)
            event = em.SpriteEvent("onFall", None, ani, 0, 0)
            sprite.em.add(event)            
            globals.spiders.append(sprite)  
        globals.camera = engine.Camera(globals.map, globals.marek, globals.window.width, globals.window.height)
		
    