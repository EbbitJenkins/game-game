import state_intro
import state_play
import state_exit
import state_menu
import state_death
import state_load

#makes things syntatically cleaner
def intro():
    return state_intro.intro()
    
def play():
    return state_play.play()

def exit():
    return state_exit.exit()

def menu():
    return state_menu.menu()

def death():
    return state_death.death()
    
def load():
    return state_load.load()
    

#NULL is an initial state, goes to INTRO
class null:
    "null"  #sort of hacky way to compare states
    def timer(self, dt):
        #this code is run the cycle after 'enter' is called and every subsequent cycle until it returns a different state (at which point leave is called)
        next_state = intro()
        #goes to intro
        return next_state
    def enter(self):
        #this code is run the cycle that the state changes TO this state
        print "enter null"
    def leave(self):
        #this code is run the cycle that the state changes FROM this state
        print "leave null"
    

