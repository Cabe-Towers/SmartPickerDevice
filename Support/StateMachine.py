# Written by Josh?

from Support.SupportFunctions import display

class StateMachine:
    def __init__(self, 
                states =['INIT', 'CALLED', 'ACCEPT', 'ARRIVED', 'LOADED'],
                initial_state = "INIT"):
        self.transistionTable = []
        self.states = states
        self.current_state = initial_state

        # States for Call a Robot #
        self.addTransition("call_robot", "INIT", "CALLED")
        self.addTransition("accepted_robot", "CALLED", "ACCEPT")
        self.addTransition("cancel_robot", "CALLED", "INIT")
        self.addTransition("cancel_accept", "ACCEPT", "INIT")
        self.addTransition("cancel_load", "ARRIVED", "INIT")
        self.addTransition("robot_arrived", "ACCEPT", "ARRIVED")
        self.addTransition("robot_loaded", "ARRIVED", "LOADED")
        self.addTransition("user_reset", "LOADED", "INIT")

    def addTransition(self, trigger, source, dest):
        if not source in self.states:
            raise Exception(source + "not a valid state.")
        if not dest in self.states:
            raise Exception(dest + "not a valid state.")
        self.transistionTable.append([trigger, source, dest])

    def trigger(self, _trigger):
        valid_trigger = False
        for row in self.transistionTable:
            if row[0] == _trigger and row[1] == self.current_state:
                valid_trigger = True
                self.current_state = row[2]
        if not valid_trigger:
            raise Exception(_trigger + "is not a valid trigger for state " + self.current_state)
        display("Now in state: " + self.current_state)

    def get_current_state(self):
        return self.current_state
    
    def get_states(self):
        return self.states
