import state

#INTRO state is for splash screens and other 'pre-menu' stuff, goes to MENU
class STATE_intro:
    "intro"
    def timer(self, dt):
        next_state = state.STATE_menu()
        return next_state
    def enter(self):
        return
    def leave(self):
        return
    