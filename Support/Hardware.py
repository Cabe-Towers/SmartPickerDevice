# Written by Josh

from machine import Pin, Timer, PWM
from Support.SupportFunctions import wait



class Hardware:
    def __init__(self, timer = 0):
        # Pins
        self.red_led = Pin(32, Pin.OUT)
        self.red_button = Pin(2, Pin.IN, Pin.PULL_UP)
        self.green_led = Pin(33, Pin.OUT)
        self.green_button = Pin(15, Pin.IN, Pin.PULL_UP)
        self.white_led = Pin(13, Pin.OUT)
        self.white_button = Pin(25, Pin.IN, Pin.PULL_UP) 

        self.buzz = PWM(Pin(12, Pin.OUT))
        self.buzz_on(5000)
        wait(1000)
        self.buzz_off()
        
        self.flash_red_led = False
        self.flash_green_led = False
        self.flash_white_led = False
        self.flash_state = 0
        
        self.timer = Timer(timer)

    #            
    def startTimer(self):
        self.timer.init(period=300, mode=Timer.PERIODIC, callback=self.flash_callback)

    def buzz_on(self, f = 5000):
        self.buzz.init(freq=f, duty=50)

    def buzz_off(self):
        self.buzz.deinit()

    def stopTimer(self):
        self.timer.deinit()

    def flash_callback(self,x):
        if self.flash_state == 1:
            if self.flash_red_led:
                self.red_led.value(1)
            if self.flash_green_led:
                self.green_led.value(1)
            if self.flash_white_led:
                self.white_led.value(1)
        elif self.flash_state == 0:
            if self.flash_red_led:
                self.red_led.value(0)
            if self.flash_green_led:
                self.green_led.value(0)
            if self.flash_white_led:
                self.white_led.value(0)
        self.flash_state = 1 - self.flash_state
        

    def set_led(self, led, val):
        if led == "red":
            self.red_led.value(val)
        elif led == "green":
            self.green_led.value(val)
        elif led == "white":
            self.white_led.value(val)
        
    def flash_led(self, led, val):
        if led == "red":
            self.flash_red_led = val
        elif led == "green":
            self.flash_green_led = val
        elif led == "white":
            self.flash_white_led = val

    def reset_led_state(self):
        self.red_led.value(0)
        self.white_led.value(0)
        self.green_led.value(0)
        self.flash_red_led = False
        self.flash_green_led = False
        self.flash_white_led = False
    
    def button_pressed(self):
        if self.red_button.value() == 0:
            return "red_pressed"
        elif self.white_button.value() == 0:
            return "white_pressed"
        elif self.green_button.value() == 0:
            return "green_pressed"
        else:
            return ""