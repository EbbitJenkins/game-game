import state
import engine

#INTRO state is for splash screens and other 'pre-menu' stuff, goes to MENU
class STATE_intro(state.State):
    def update(self, dt):
        next_state = engine.STATE_menu()
        return next_state
    def enter(self):
        return
    def leave(self):
        return
    