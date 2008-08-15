# State base class
class State:
    def __init__(self, name):
        self._name = name
        self._timer = 0
    def __repr__(self):
        return str(self._name)
    def __cmp__(self, other):
        return cmp(self._name, other._name)
    def update(self, dt):
        # This code is run the cycle after 'enter' is called and every subsequent cycle 
        # until it returns a different state (at which point leave is called).
        self._timer = self._timer + dt
        return self
    def enter(self):
        # This code is run the cycle that the FSM changes TO this state
        pass
    def leave(self):
        # This code is run the cycle that the FSM changes FROM this state
        pass    

