import state
import player
import fsm

#LOAD state is for loading a map, as well as everything involved with the map.  Goes to PLAY
class load:
    "load"
    def timer(self, dt):
        next_state = state.play()
        self.init()  #initialize stuffs!
        return next_state
    def enter(self):
        print "enter load"
    def leave(self):
        print "leave load"
    def init(self):
        fsm.player = player.player(2, 5)    #initialize the player object 
    