import state
import engine
import globals

#PLAY state is for 'normal' gameplay, such as running around causing mayhem
#goes to DEATH when the marek runs out of lives
class STATE_play(state.State):
    def update(self, dt):
        next_state = self
        if not (globals.marek.curr_state.__doc__ == "death" and globals.marek.lives < 1):
            self._timer = self._timer + dt
            globals.camera.update()				#Do camera, graphical stuff
            globals.marek.do_timer(dt) 				#Do player stuff
            for spider in globals.spiders:
                spider.update(dt)                   # Do spider stuff
        else:
            #marek is in the DEATH state and has no lives left, thus game over
            next_state = engine.STATE_death()
        return next_state
    def enter(self):
        print "enter play"
        self._timer = 0
    def leave(self):
        print "leave play"