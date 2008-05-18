import fsm

#PLAYER object will handle everything that the player does; it is instantiated in fsm as a global
#NPC objects could be very similar to this
class player:
    def __init__(self, x, y):
        self.curr_state = null()    #initializes the state for the player's FSM
        self.hp = 100
        self.lives = 3
        self.dx = x
        self.dy = y
        
    def do_timer(self, dt):
        print self.hp
        #runs the player FSM - no return is necissary since do_state has access to self.curr_state
        self.do_state(self.curr_state.timer(dt))
        
    def do_state(self, next_state):
        if not (next_state == self.curr_state):
            self.curr_state.leave()
            
            self.curr_state = next_state
            
            self.curr_state.enter()
        return self.curr_state

#NULL is an initial state, goes to NEW
class null:
    "null"
    def timer(self, dt):
        next_state = new()
        return next_state
    def enter(self):
        print "enter player.null"
    def leave(self):
        print "leave player.null"

#IDLE runs while nothing else is going on in this FSM
#In theory, there will be 3-4 more FSM being run from within idle.timer, controlling movement, attacks, collision and (in the case of NPC) AI
class idle:
    "idle"
    def timer(self, dt):
        next_state = self
        if fsm.player.hp == 0:
            #since the player has no more hp, go to death state
            next_state = death()
        if fsm.player.hp > 0:
            #since the player still has hp, leave next_state as self
            fsm.player.hp = fsm.player.hp - 25
        return next_state
    def enter(self):
        print "enter player.idle"
    def leave(self):
        print "leave player.idle"
    
#NEW initializes the player object to default conditions, such as when you come back from death
#goes to IDLE
class new:
    "new"
    def timer(self, dt):
        next_state = idle()
        fsm.player.hp = 100
        return next_state
    def enter(self):
        print "enter player.new"
    def leave(self):
        print "leave player.new"

#DEATH removes a life and goes back to NEW
class death:
    "death"
    def timer(self, dt):
        next_state = new()
        return next_state
    def enter(self):
        print "enter player.death"
        fsm.player.lives = fsm.player.lives - 1
        print "LIVES REMAINING: %d" % (fsm.player.lives, )
    def leave(self):
        print "leave player.death"
        