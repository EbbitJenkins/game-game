import state
import fsm
import globals

#PLAY state is for 'normal' gameplay, such as running around causing mayhem
#goes to DEATH when the marek runs out of lives
class STATE_play:
    "play"
    def timer(self, dt):
        next_state = self
        if not (globals.marek.curr_state.__doc__ == "death" and globals.marek.lives < 1):
            self.count = self.count + dt
            globals.camera.update()				#Do camera, graphical stuff
            #globals.map.update(self.x, self.y)	
			#TODO: Do AI stuff
            globals.marek.do_timer(dt) 				#Do player stuff
            for spider in globals.spiders:
                spider.update(dt)                   # Do spider stuff
        else:
            #marek is in the DEATH state and has no lives left, thus game over
            next_state = state.STATE_death()
        return next_state
    def enter(self):
        print "enter play"
        self.count = 1
    def leave(self):
        print "leave play"