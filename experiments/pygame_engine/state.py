import state_play
import state_load

#makes things syntatically cleaner
def STATE_play():
    return state_play.STATE_play()

def STATE_load():
    return state_load.STATE_load()
    

#NULL is an initial state, goes to INTRO
class STATE_null:
    "null"  #sort of hacky way to compare states
    def timer(self, dt):
        #this code is run the cycle after 'enter' is called and every subsequent cycle until it returns a different state (at which point leave is called)
        next_state = STATE_load()
        #goes to intro
        return next_state
    def enter(self):
        #this code is run the cycle that the state changes TO this state
        print "enter null"
    def leave(self):
        #this code is run the cycle that the state changes FROM this state
        print "leave null"
    

