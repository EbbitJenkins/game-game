import state

#MENU state is for the 'Start Game' screen, goes to LOAD or EXIT depending on input
class STATE_menu:
    "menu"
    def timer(self, dt):
        next_state = self
        next_state = state.STATE_load()
        return next_state
    def enter(self):
        print "enter menu"
    def leave(self):
        print "leave menu"
        