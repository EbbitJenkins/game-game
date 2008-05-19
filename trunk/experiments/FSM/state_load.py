import state
import marek
import fsm

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
        fsm.marek = marek.marek(2, 5)    #initialize the marek object 
    