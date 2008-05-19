import state

#INTRO state is for splash screens and other 'pre-menu' stuff, goes to MENU
class STATE_intro:
    "intro"
    def timer(self, dt):
        next_state = state.STATE_menu()
        return next_state
    def enter(self):
        print "enter intro"
    def leave(self):
        print "leave intro"
    