import state
import fsm

#PLAY state is for 'normal' gameplay, such as running around causing mayhem
#goes to DEATH when the player runs out of lives
class play:
    "play"
    def timer(self, dt):
        next_state = self
        if not (fsm.player.curr_state.__doc__ == "death" and fsm.player.lives < 1):
            #player is alive still
            print "cycle %d" % (self.count, ) 
            self.count = self.count + dt
            fsm.player.do_timer(dt) #handles player stuff, including its own FSM
        else:
            #player is in the DEATH state and has no lives left, thus game over
            next_state = state.death()
        return next_state
    def enter(self):
        print "enter play"
        self.count = 1
    def leave(self):
        print "leave play"