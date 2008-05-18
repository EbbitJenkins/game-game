import state
import player
import fsm

class play:
	"play"
	def timer(self, dt):
		next_state = self
		if not (fsm.player.curr_state.__doc__ == "death" and fsm.player.lives < 1):
			print "cycle %d" % (self.count, ) 
			self.count = self.count + dt
			fsm.player.do_timer(dt)
		else:
			next_state = state.death()
		return next_state
	def enter(self):
		print "enter play"
		self.count = 1
		fsm.player = player.player(2, 5)
	def leave(self):
		print "leave play"