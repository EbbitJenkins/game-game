import state

class death:
    "death"
    def timer(self, dt):
        return state.menu()
    def enter(self):
        print "enter death"
    def leave(self):
        print "leave death"