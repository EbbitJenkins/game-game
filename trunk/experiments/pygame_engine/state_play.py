import state
import fsm
import globals

#PLAY state is for 'normal' gameplay, such as running around causing mayhem
#goes to DEATH when the marek runs out of lives
class STATE_play:
    "play"
    def timer(self, dt):
        next_state = self
        if not globals.player.lives < 1:
            self.count = self.count + dt
            globals.player.update(dt) 				#Do player stuff
        return next_state
    def enter(self):
        print "enter play"
        self.count = 1
    def leave(self):
        print "leave play"