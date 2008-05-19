import marek_move
import fsm


#MAREK object will handle everything that marek does; it is instantiated in fsm as a global
#other sprite objects could be very similar to this
class marek:
    def __init__(self, x, y):
        self.curr_state = null()    #initializes the state for the marek's FSM
        self.move_state = marek_move.move()
        self.moves = moves()    #used to access list of move states
        self.hp = 100           #marek's current hp
        self.hp_max = 100       #max hp marek currently can have
        self.lives = 3          #times that marek can die
        self.dx = 0             #directional x-vector, max 1, min -1
        self.dy = 0             #directional y-vector, max 1, min -1
        self.x = x              #position on x-axis
        self.y = y              #position on y-axis
        self.run_speed = 1      #how fast marek runs
        self.jump_height = 2    #how long marek can jump for, in seconds
        
    def do_timer(self, dt):
        print self.hp
        #runs the marek FSM - no return is necissary since do_state has access to self.curr_state
        self.do_state(self.curr_state.timer(dt))
        
    def do_state(self, next_state):
        if not (next_state == self.curr_state):
            self.curr_state.leave()
            
            self.curr_state = next_state
            
            self.curr_state.enter()
        return self.curr_state
        
    def move(self, dx, dy):
        #actual drawing of the sprite will be handled elsewhere
        self.x = self.x + (dx * self.run_speed)
        self.y = self.y + (dy * self.run_speed)
    

#NULL is an initial state, goes to NEW
class null:
    "null"
    def timer(self, dt):
        next_state = new()
        return next_state
    def enter(self):
        print "enter marek.null"
    def leave(self):
        print "leave marek.null"

#IDLE runs while nothing else is going on in this FSM
#In theory, there will be 3-4 more FSM being run from within idle.timer, controlling movement, attacks, collision and (in the case of NPC) AI
class idle:
    "idle"
    def timer(self, dt):
        next_state = self
        if fsm.marek.hp == 0:
            #since the marek has no more hp, go to death state
            next_state = death()
        if fsm.marek.hp > 0:
            fsm.marek.move_state.do_state(fsm.marek.move_state.curr_state.timer(dt))
            fsm.marek.hp = fsm.marek.hp - 25
        return next_state
    def enter(self):
        print "enter marek.idle"
    def leave(self):
        print "leave marek.idle"
    
#NEW initializes the marek object to default conditions, such as when you come back from death
#goes to IDLE
class new:
    "new"
    def timer(self, dt):
        next_state = idle()
        fsm.marek.hp = fsm.marek.hp_max
        fsm.marek.move_state.action = fsm.marek.moves.idle()
        return next_state
    def enter(self):
        print "enter marek.new"
    def leave(self):
        print "leave marek.new"

#DEATH removes a life and goes back to NEW
class death:
    "death"
    def timer(self, dt):
        next_state = new()
        return next_state
    def enter(self):
        print "enter marek.death"
        fsm.marek.lives = fsm.marek.lives - 1
        print "LIVES REMAINING: %d" % (fsm.marek.lives, )
    def leave(self):
        print "leave marek.death"
        
#Used to access move states
class moves:
    def null(self):
        return marek_move.null()
    def idle(self):
        return marek_move.idle()
    def jump(self):
        return marek_move.jump()