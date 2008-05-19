import fsm

class move:
    def __init__(self):
        self.curr_state = STATE_null()
        self.action = STATE_idle()
               
    def do_state(self, next_state):
        if not (next_state == self.curr_state):
            self.curr_state.leave()
            
            self.curr_state = next_state
            
            self.curr_state.enter()
        return self.curr_state

class STATE_null:
    "null"
    def timer(self, dt):
        return STATE_idle()
    def enter(self):
        print "entering marek.move_state.null"
        pass
    def leave(self):
        print "leaving marek.move_state.null"
        pass

class STATE_idle:
    "idle"
    def timer(self, dt):
        next_state = self
        #move_state.action is what the user wants to do - it will be set by the keyboard event
        if fsm.marek.move_state.action.__doc__ == "idle":
            if fsm.marek.dx != 0:
                #move in x-axis
                fsm.marek.move(fsm.marek.dx, 0)
            else:
                if fsm.marek.dy == 0:
                    #TODO: run idle animation
                    #if dy != 0, he is falling or something - not idle
                    pass
            if fsm.marek.dy != 0:
                if fsm.marek.dy < 0:
                    #TODO: run falling animation
                    pass
                else:
                    #TODO: run falling up animation?
                    pass
                #move in y-axis
                fsm.marek.move(0, fsm.marek.dy)
        else:
            next_state = fsm.marek.move_state.action
        return next_state
        
    def enter(self):
        print "entering marek.move_state.idle"
        pass
        
    def leave(self):
        print "leaving marek.move_state.idle"
        pass
    
class STATE_jump:
    "jump"
    def timer(self, dt):
        next_state = self
        jump.timer = jump.timer + dt
        if jump.timer < fsm.marek.jump_height and fsm.marek.move_state.action.__doc__ == "jump":
            #jump_height is seconds that marek can jump for
            fsm.marek.dy = fsm.marek.dy - fsm.marek.dy/15
            fsm.marek.move(0, fsm.marek.dy)
            if fsm.marek.dx != 0:
                fsm.marek.move(fsm.marek.dx, 0)
        else:
            if fsm.marek.move_state.action.__doc__ == "jump":
                next_state = idle()
            else:
                next_state = fsm.marek.move_action.action
        return next_state
         
    def enter(self):
        jump.timer = 0  #keeps track of how long we have been in jump state
    def leave(self):
        pass
        