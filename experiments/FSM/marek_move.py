import globals

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
        print "enter marek.move.null"
    def leave(self):
		print "leave marek.move.null"
		
class STATE_idle:
    "idle"
    def timer(self, dt):
        next_state = self        
        #move_state.action is what the user wants to do - it will be set by the keyboard event
        if globals.marek.move_state.action.__doc__ == "idle":
            if globals.marek.dx != 0:
                #move in x-axis
                if not self.runFlag:
                    print "Running dx: " + str(globals.marek.dx)
                    self.runFlag = True
                if globals.marek.dx < 0:
                    globals.marek.image = globals.marek.images['stand_left']
                if globals.marek.dx > 0:
                    globals.marek.image = globals.marek.images['stand_right']
                globals.marek.move(globals.marek.dx, 0, dt)
            else:
                if self.runFlag:
                    print "Stopped running"
                    self.runFlag = False
                if globals.marek.dy == 0:
                    #TODO: run idle animation?
                    pass
            if globals.marek.dy != 0:
                if globals.marek.dy < 0:
                    #TODO: run falling animation
                    print "Start falling"
                    pass
                else:
                    print "Start jumping"
                    #TODO: run falling up animation?
                    pass
                #move in y-axis
                globals.marek.move(0, globals.marek.dy, dt)
        else:
            next_state = globals.marek.move_state.action
        return next_state
        
    def enter(self):
        print "enter marek.move.idle"
        self.runFlag = False  #debug
        
    def leave(self):
		print "leave marek.move.idle"
    
class STATE_jump:
    "jump"
    def timer(self, dt):
        next_state = self
        self.time = self.time + dt
        self.limit = self.limit + dt        
        print "time: " + str(self.time) + ", height: " + str(globals.marek.jump_height)
        if self.time < globals.marek.jump_height and globals.marek.move_state.action.__doc__ == "jump":
            #jump_height is seconds that marek can jump for
            if self.limit > (globals.marek.jump_height * .1):
                print "decrease"
                self.limit = 0
                globals.marek.dy = globals.marek.dy - globals.marek.dy/5   #ascent gets slower as you go up                
            globals.marek.move(0, globals.marek.dy, dt)
            if globals.marek.dx != 0:
                #move left/right
                globals.marek.move(globals.marek.dx, 0, dt)
        else:
            #either the jump is over or another action wants to happen
            globals.marek.dy = 0 
            if globals.marek.move_state.action.__doc__ == "jump":  
                globals.marek.move_state.action = globals.marek.moves.STATE_idle()  #reset action to idle, so we aren't jumping forever
                next_state = globals.marek.moves.STATE_idle()   #next state to idle, since no other action has been given
            else:
                #some other action wants to be done, so return it
                next_state = globals.marek.move_state.action
        return next_state
    def enter(self):
        print "enter marek.move.jump"
        self.time = 0  #keeps track of how long we have been in jump state
        self.limit = 0  #used to control how quickly ascent slows        
        globals.marek.dy = globals.marek.jump_speed
    def leave(self):
        print "enter marek.move.jump"
        