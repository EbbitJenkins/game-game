import globals
import engine
import state
import marek
import sys

#LOAD state is for loading a map, as well as everything involved with the map.  Goes to PLAY
class STATE_load:
    "load"
    def timer(self, dt):
        next_state = state.STATE_play()
        self.init()  #initialize stuffs!
        return next_state
    def enter(self):
        print "enter load"
    def leave(self):
        print "leave load"
    def init(self):	    
        globals.marek = marek.marek(120, 100, 100)    #initialize the marek object 
        globals.camera = engine.Camera(globals.map, globals.marek, globals.window.width, globals.window.height)
		
    