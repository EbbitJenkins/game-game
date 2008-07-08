import state
import sys

#EXIT state is for leaving the game all together, ends the process
class STATE_exit(state.State):
    def update(self, dt):
        sys.exit()
    def enter(self):
        print "enter exit"
    def leave(self):
        print "leave exit"