# Finite State Machine base class
class FSM:
    def __init__(self, state):
        self.curr_state = state
        self.action = None
    def do_state(self, next_state):
        #check if there is a new state
        if not (next_state == self.curr_state):
            #leave the old one
            self.curr_state.leave()
            #make the new one, the current one
            self.curr_state = next_state
            #enter the new one!
            self.curr_state.enter()
        