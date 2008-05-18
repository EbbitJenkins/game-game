import state

class intro:
    "intro"
    def timer(self, dt):
        return state.menu()
    def enter(self):
        print "enter intro"
    def leave(self):
        print "leave intro"
    