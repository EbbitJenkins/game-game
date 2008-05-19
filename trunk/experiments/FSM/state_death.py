import state

#DEATH state is for game over, goes back to the menu
class STATE_death:
    "death"
    def timer(self, dt):
        next_state = state.STATE_menu()
        return next_state
    def enter(self):
        print "enter death"
    def leave(self):
        print "leave death"