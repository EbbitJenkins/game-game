import state
import sys

class exit:
	"exit"
	def timer(self, dt):
		sys.exit()
	def enter(self):
		print "enter exit"
	def leave(self):
		print "leave exit"