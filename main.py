import time
from Config import CLIENT_ID
import network
from sys import exit
from Support.StateMachine import StateMachine
from Support.SIM7000G import SIM7000G
from Support.SupportFunctions import wait, display
from Support.Hardware import Hardware
from machine import Pin, Timer, PWM

########
# Main #
########
class Main:
    def __init__(self, user):
        self.state = "INIT"
        self.previousState = ""
        display("INIT HARDWARE")
        self.hardware = Hardware()
        display("INIT STATE MACHINE")
        #self.state_machine = StateMachine()
        self.user_name =  "STD_v2_" + user.decode('utf-8')
        display("INIT MODEM")
        self.hardware.startTimer()
        self.hardware.flash_led("red", True)
        self.modem = SIM7000G(user_name=self.user_name, update_orders_cb=self.update_orders_cb)
        
        # Connect GPS
        self.hardware.flash_led("green", True)
        display("INIT GPS")
        self.modem.initGPS()

        # Connect to CAR server.
        self.hardware.flash_led("white", True)
        
        display("REGISTER")
        self.modem.registerBack()

        self.hardware.reset_led_state()
        self.hardware.stopTimer()

    #########
    # start #
    #########
    def start(self):
        display("User Name: " + self.user_name)
        display("Welcome to Call a Robot.")
        self.hardware.startTimer()
        while True:

            # Check if button has been pressed
            event = self.hardware.button_pressed()
            #print("State: ", self.state)
            if event:
                if event == "red_pressed":
                    while self.hardware.button_pressed() == "red_pressed":
                        wait(50)
                    self.red_pressed()
                elif event ==  "white_pressed":
                    while self.hardware.button_pressed() == "white_pressed":
                        wait(50)
                    self.white_pressed()
                elif event == "green_pressed":
                    while self.hardware.button_pressed() == "green_pressed":
                        wait(50)
                    self.green_pressed()
            wait(50)
            if self.previousState != self.state:
                self.indicate()
            if self.state == "INIT" or self.state == "REGISTERED" or self.state == "CONNECTED":
                self.ledsOff()

    ###############
    # red_pressed #
    ###############
    def red_pressed(self):
        display("Red Pressed")
        self.hardware.reset_led_state()
        self.modem.stopTimer()
        self.hardware.set_led("red", 1)
        self.modem.cancel_robot()
        display("Robot Cancelled.")
        self.hardware.buzz_on()
        wait(500)
        self.hardware.buzz_off()
        self.hardware.set_led("red", 0)
        self.modem.startTimer()

    ################
    # gree_pressed #
    ################
    def green_pressed(self):
        display("Green Pressed")
        self.hardware.reset_led_state()
        self.modem.stopTimer()
        self.hardware.set_led("green", 1)
        self.modem.call_robot()
        display("Robot Called.")
        self.hardware.buzz_on()
        wait(500)
        self.hardware.buzz_off()
        self.hardware.set_led("green", 0)
        self.modem.startTimer()

    #################
    # white pressed #
    #################
    def white_pressed(self):
        display("Green Pressed")
        self.hardware.reset_led_state()
        self.modem.stopTimer()
        self.hardware.set_led("white", 1)
        self.modem.set_loaded()
        display("Robot Loaded.")
        self.hardware.buzz_on()
        wait(500)
        self.hardware.buzz_off()
        self.hardware.set_led("white", 0)
        #self.modem.cancel_robot()
        self.ledsOff()
        self.modem.startTimer()

    ####################
    # update_orders_cb #
    ####################
    def update_orders_cb(self, state):
        """ Recieves the state from server. Updates the state machine."""
        # Two tone signal
        self.hardware.buzz_on(5000)
        wait(500)
        self.hardware.buzz_off()
        wait(250)
        self.hardware.buzz_on(5000)
        wait(500)
        self.hardware.buzz_off()
        self.previousState = self.state
        self.state = state

    ############
    # indicate #
    ############
    def indicate(self):
        if self.state == "ACCEPT":
            self.hardware.flash_led("green", True)
        elif self.state == "ARRIVED":
            self.hardware.set_led("green", 1)
            self.hardware.flash_led("green", False)
            self.hardware.flash_led("white", True)
        elif self.state == "CALLED":
            self.hardware.set_led("green", 1)
            self.hardware.flash_led("green", False)
        elif self.state == "INIT":
            self.ledsOff()
        elif self.state == "REGISTERED":
            self.hardware.flash_led("green", True)
            self.hardware.flash_led("white", True)
            self.hardware.flash_led("red", True)            

    ###########
    # ledsOff #
    ###########
    def ledsOff(self):
        self.hardware.set_led("green", 0)
        self.hardware.set_led("red", 0)
        self.hardware.set_led("white", 0)
        self.hardware.flash_led("green", False)
        self.hardware.flash_led("white", False)
        self.hardware.flash_led("red", False)

    ############
    # shutdown #
    ############
    def shutdown(self):
        self.hardware.reset_led_state()
        self.hardware.reset_event()
        # Andy added
        self.hardware.timer = None
        self.modem.timer = None
        self.modem.shutdown()
        raise SystemExit

if __name__ == "__main__":
    display("IN MAIN")
    m = Main(CLIENT_ID)
    try:
        m.start()
    except KeyboardInterrupt: 
        display("Exiting")
        m.shutdown()