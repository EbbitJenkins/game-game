import state
import engine

#DEATH state is for game over, goes back to the menu
class STATE_death(state.State):
    def update(self, dt):
        next_state = engine.STATE_menu()
        return next_state
    def enter(self):
        print "enter death"
    def leave(self):
        print "leave death"