import state

#DEATH state is for game over, goes back to the menu
class death:
    "death"
    def timer(self, dt):
        next_state = state.menu()
        return next_state
    def enter(self):
        print "enter death"
    def leave(self):
        print "leave death"