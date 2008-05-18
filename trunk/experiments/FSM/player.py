import fsm

class player:
    def __init__(self, x, y):
        self.curr_state = null()
        self.hp = 100
        self.lives = 3
        self.dx = x
        self.dy = y
        
    def do_timer(self, dt):
        print self.hp
        self.do_state(self.curr_state.timer(dt))
        
    def do_state(self, next_state):
        if not (next_state == self.curr_state):
            self.curr_state.leave()
            
            self.curr_state = next_state
            
            self.curr_state.enter()
        return self.curr_state

class null:
    "null"
    def timer(self, dt):
        next_state = new()
        return next_state
    def enter(self):
        print "enter player.null"
    def leave(self):
        print "leave player.null"

class idle:
    "idle"
    def timer(self, dt):
        next_state = self
        if fsm.player.hp == 0:
            next_state = death()
        if fsm.player.hp > 0:
            fsm.player.hp = fsm.player.hp - 25
        return next_state
    def enter(self):
        print "enter player.idle"
    def leave(self):
        print "leave player.idle"
    
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
        