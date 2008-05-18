#/usr/bin/env python

import state

global player

def do_state(curr_state, next_state):
	if not (next_state == curr_state):
		curr_state.leave()
		
		curr_state = next_state
		
		curr_state.enter()
	
	return curr_state
    
if __name__ == '__main__':
	curr_state = state.null()
	while True:
		curr_state = do_state(curr_state, curr_state.timer(1))