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
                    #TODO: Run to the left animation
                    globals.marek.image = globals.marek.images['stand_left']
                if globals.marek.dx > 0:
                    #TODO: Run to the right animation
                    globals.marek.image = globals.marek.images['stand_right']
            else:
                if self.runFlag:
                    print "Stopped running"
                    self.runFlag = False
                if globals.marek.dy == 0:
                    #TODO: run idle animation?
                    pass
            if globals.marek.isCollision():
                globals.marek.move_state.action = globals.marek.moves.STATE_fall()
                next_state = globals.marek.move_state.action
        else:
            next_state = globals.marek.move_state.action
        return next_state
        
    def enter(self):
        print "enter marek.move.idle"
        self.runFlag = False  #debug
        globals.marek.dy = -globals.marek.weight
    def leave(self):
		print "leave marek.move.idle"        
class STATE_fall:
    "fall"
    def timer(self, dt):
        next_state = self
        self.limit = self.limit + dt
        if globals.marek.move_state.action.__doc__ == "fall":
            if globals.marek.isCollision():
                # Hit the ground
                print "next state = idle"
                globals.marek.move_state.action = globals.marek.moves.STATE_idle()               
                next_state = globals.marek.move_state.action
            else:
                if self.limit > (globals.marek.jump_height * .1):
                    self.limit = 0
                    globals.marek.dy = globals.marek.dy - globals.marek.jump_speed/5
        else:
            next_state = globals.marek.move_state.action
        if globals.marek.dx != 0:
            if globals.marek.dx > 0:
                globals.marek.dx = globals.marek.jump_arc
            else:
                globals.marek.dx = -globals.marek.jump_arc
        return next_state
    def enter(self):
        print "enter marek.move.fall"
        self.limit = 0  # Controls acceleration
        globals.marek.dy = -globals.marek.weight
    def leave(self):
        print "leave marek.move.fall"
        globals.marek.dy = -globals.marek.weight
class STATE_jump:
    "jump"
    def timer(self, dt):
        next_state = self
        self.time = self.time + dt
        self.limit = self.limit + dt        
        print "time: " + str(self.time) + ", height: " + str(globals.marek.jump_height)        
        if globals.marek.move_state.action.__doc__ == "jump" and self.time < globals.marek.jump_height:
            # jump_height is seconds that marek can jump for
            # Ascending
            if self.limit > (globals.marek.jump_height * .1):
                print "decrease ascent"
                self.limit = 0
                globals.marek.dy = globals.marek.dy - globals.marek.jump_speed/5   #ascent gets slower as you go up                
        else:
            print "next state: " + str(globals.marek.move_state.action.__doc__)
            if globals.marek.move_state.action.__doc__ == "jump":
                globals.marek.move_state.action = globals.marek.moves.STATE_fall()
            next_state = globals.marek.move_state.action
        if globals.marek.dx != 0:
            # move left/right
            if globals.marek.dx > 0:
                globals.marek.dx = globals.marek.jump_arc
            else:
                globals.marek.dx = -globals.marek.jump_arc
        return next_state
    def enter(self):
        print "enter marek.move.jump"
        self.time = 0  #keeps track of how long we have been in jump state
        self.limit = 0  #used to control how quickly ascent slows        
        globals.marek.dy = globals.marek.jump_speed
    def leave(self):
        print "enter marek.move.jump"
        globals.marek.dy = 0
        