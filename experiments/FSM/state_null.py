import state
import engine

# NULL is an initial state, goes to INTRO
class STATE_null(state.State):
    def update(self, dt):        
        next_state = engine.STATE_intro()
        return next_state
    def enter(self):        
        print "enter null"
    def leave(self):        
        print "leave null"
