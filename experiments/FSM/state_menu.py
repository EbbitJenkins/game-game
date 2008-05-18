import state

class menu:
	"menu"
	def timer(self, dt):
		num = raw_input("1) Play game \n2) Exit \n")
		if num == "1":
			return state.load()
		else:
			return state.exit()
	def enter(self):
		print "enter menu"
	def leave(self):
		print "leave menu"