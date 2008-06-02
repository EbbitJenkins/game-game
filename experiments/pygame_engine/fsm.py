#/usr/bin/env python

import state

global curr_state

def do_state(curr_state, next_state):
    #check if there is a new state
    if not (next_state == curr_state):
        #since there is, leave the old one
        curr_state.leave()
        #make the new one, the current one
        curr_state = next_state
        #enter the new one!
        curr_state.enter()
    #either way, return the current state so that we remember
    return curr_state
    