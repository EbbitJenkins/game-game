#/usr/bin/env python

import state

global marek   #because everything needs access to it

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
    
if __name__ == '__main__':
    #initialize the current state
    curr_state = state.null()
    while True:
        #timer(dt) returns either 'self' or a new state
        #dt should really be the time since this was last run, in seconds
        curr_state = do_state(curr_state, curr_state.timer(1))