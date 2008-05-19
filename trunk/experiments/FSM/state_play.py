import state
import fsm

#PLAY state is for 'normal' gameplay, such as running around causing mayhem
#goes to DEATH when the marek runs out of lives
class STATE_play:
    "play"
    def timer(self, dt):
        next_state = self
        if not (fsm.marek.curr_state.__doc__ == "death" and fsm.marek.lives < 1):
            #marek is alive still
            print "cycle %d" % (self.count, ) 
            self.count = self.count + dt
            fsm.marek.do_timer(dt) #handles marek stuff, including its own FSM
        else:
            #marek is in the DEATH state and has no lives left, thus game over
            next_state = state.STATE_death()
        return next_state
    def enter(self):
        print "enter play"
        self.count = 1
    def leave(self):
        print "leave play"