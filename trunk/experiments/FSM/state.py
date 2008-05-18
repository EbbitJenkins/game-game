import state_intro
import state_play
import state_exit
import state_menu
import state_death
import state_load

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
    

class null:
    "null"
    def timer(self, dt):
        return intro()
    def enter(self):
        print "enter null"
    def leave(self):
        print "leave null"
    

