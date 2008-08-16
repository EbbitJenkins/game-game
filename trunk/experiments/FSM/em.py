import itertools
#  Currently used in spider example
class EventMachine: 
    def __init__(self, sprite=None):
        self.active_events = []
        self.events = {}
        self._sprite = sprite
        
    def notify(self, event_name, command="start"):
        if command == "start":
            self.events[event_name].activate()
        if command == "end":
            self.events[event_name].deactivate()
    
    #  Usage - @EventMachine.event
    #             -  def eventName:
    def event(self, func):
        #_event = SpriteEvent(func)
        #self.events[func.__name__] = _event
        #  TODO:  Once manifest stuff is in, this function will be:
        self.events[func.__name__].set_event(func)
        
    #  TODO:  This will be used to load manifest-created event objects into the
    #   EventMachine.  event(func) will be used to fill in any code to be run during the event
    #  Animation and name information will be from manifest files
    def add(self, event):
        self.events[event.__name__] = event
        
    #  Executes all active events
    def update(self):
        for name, event in self.events.iteritems():
            if event:
                event(self._sprite)
            
#  TODO:  Use this for signaling the end of events to states -- need to make a handler in FSM
class SimpleEvent:
    def __init__(self, name='blank', data=None):
        self.__name__ = name
        self._data = data
        
    def __call__(self):
        return self._data
        
#  An event without animation support.  Currently used.
class Event:
    def __init__(self, name='blank', event=None):
        self.__name__ = name
        self._event = event
        self._timer = 0
        self._isActive = False
        
    def set_event(self, event):
        self._event = event

    def reset_timer(self):
        self._timer = 0        
        
    def activate(self):
        self._isActive = True
        
    def deactivate(self):
        self._timer = 0
        self._isActive = False
        
    def __nonzero__(self):
        return self._isActive
        
    def __call__(self, *args):        
        self._event(self, *args)       
        self._timer = self._timer + 1

#  TODO:  Create these from the manifest and then add them to the EventMachine using add. 
#  The main stuff that will be in the manifest (as of now) is:
#  animation = image file that contains the frames of the animation
#  pre = number of frames to run before running the event code
#  post = number of frames to run after stopping the event code
#  loop = boolean of whether or not the animation should loop
#  ---------
#  event = function describing what to do during this event (this function will be passed the sprite as an arg)
class SpriteEvent(Event):
    def __init__(self, name='blank', event=None, animation=None, pre=0, post=0, loop=True):
        self.__name__ = name
        self._event = event
        self._animation = animation
        self._frame = 0
        self._pre = pre
        self._post = post
        self._timer = 0
        self._isActive = False
        
    def deactivate(self):
        self._timer = 0
        self._frame = 0
        self._isActive = False
               
    def set_pre(self, frame_count=0):
        self._pre = frame_count
        
    def set_post(self, frame_count=0):
        self._post = frame_count
        
    def set_animation(self, animation=None):
        self._animation = animation
                
    def __call__(self, *args):     
        if self._frame < self._pre or not self._isActive and self._frame < self._animation.end:
            self._animation(self, *args)
            self._frame = self._frame + 1
        else:
            self._animation(self, *args)            
            self._event(self, *args)    
            self._frame = self._frame + 1            
            self._timer = self._timer + 1            
        
#  TODO:  Initialize these from the manifest and add them to their respective events (example in state_load.py)
class Animation:
    def __init__(self, images):
        self._images = images
        self._iter = itertools.cycle(iter(images))
        self.end = self._images.count
        
    def step_frame(self, event, sprite):
        sprite.image = self._iter.next()
        sprite._width = sprite.image.width
        sprite._height = sprite.image.height
        
    def __call__(self, *args):
        self.step_frame(*args)       
        