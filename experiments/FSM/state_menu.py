import state
import engine

#MENU state is for the 'Start Game' screen, goes to LOAD or EXIT depending on input
class STATE_menu(state.State):
    def update(self, dt):
        next_state = engine.STATE_load()
        return next_state
    def enter(self):
        print "enter menu"
    def leave(self):
        print "leave menu"
        