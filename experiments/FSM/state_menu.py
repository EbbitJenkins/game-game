import state

#MENU state is for the 'Start Game' screen, goes to LOAD or EXIT depending on input
class STATE_menu:
    "menu"
    def timer(self, dt):
        next_state = self
        num = raw_input("1) Play game \n2) Exit \n")
        if num == "1":
            next_state = state.STATE_load()
        else:
            next_state = state.STATE_exit()
        return next_state
    def enter(self):
        print "enter menu"
    def leave(self):
        print "leave menu"