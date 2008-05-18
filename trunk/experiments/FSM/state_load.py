import state

class load:
    "load"
    def timer(self, dt):
        return state.play()
    def enter(self):
        print "enter load"
    def leave(self):
        print "leave load"
    