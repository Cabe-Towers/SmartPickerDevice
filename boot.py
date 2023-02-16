# Andy Perrett (PER18684092)
# Date: April 2022
# For Smart Trolley / Call-A-Robot
# Comments should reveal all :)
#

import utime as time
from machine import UART, Pin, reset, PWM
from Support.BootFunctions import *
from Support.WiFi import WiFi
from Support.Hardware import Hardware
from Support.SupportFunctions import wait, display

hardware = Hardware(2)

hardware.set_led("red", 0)
hardware.set_led("white", 0)
hardware.set_led("green", 0)

# Setup hardware pins
display("Enabling Power")
GSM_PWR = Pin(4, Pin.OUT) # PIN 4 on ESP32 controls power of Simcom.
GSM_PWR.value(1)  
wait(200)
GSM_PWR.value(0)
wait(200)
GSM_PWR.value(1)

# Buzzer
hardware.buzz_on()
wait(3000)
hardware.buzz_off()
hardware.flash_led("red", True)
hardware.startTimer()

# Allow time to sort itself out
display("Waiting 1 second")
wait(1000)

# TODO Not sure we need this but it does no harm
# NOTE The intended behaviour is to reset the SIM7000G chip
display("Resetting SIM7000G - maybe?")
GSM_PWR = Pin(5, Pin.OUT)    # PIN 5 resets.
GSM_PWR.value(0)  
wait(300)
GSM_PWR.value(1)

# Allow time to sort itself out
display("Waiting 1 second")
wait(1000)

##################
# Find baud rate #
##################
# We don't know what state the UART is in because the baud rate
# may have changed and is saved (if on battery).
# So we try and find the baud rate that responds without garbage
display("Setting up UART")
# NOTE LoBo (this is typical between Micropython versions!) UART
# takes different params to standard MicroPython - there may be comments
# regards buffers and timouts - LoBo doesn't use these params
serial = UART(1,baudrate=300, bits=8, parity=None, stop=1, rx=26, tx=27)

# Buffer size is 1024 across rx and tx
# both __init__ and .init() have same params for LoBo, for
# std MicroPython UART(1) suffices followed by init(params).
# Both lines kept for quick editing if we switch back to
# standard MicroPython.
serial.init(baudrate=300, bits=8, parity=None, stop=1, rx=26, tx=27)
count = 0
reply = ["XYZ"]
while "OK" not in reply:
    reply = findBaudRate(serial)
    count += 1
    if count >= 3:
        # We shouldn't need more than 1 but during testing
        # it was seen that odd things happen when you cntrl-c
        # and trying 3 times sorted.
        reset()

###########################
# Set baud rate to target #
###########################
# Getting this far means we can send commands and read response.
# Set to our target baud rate within config file.
if "OK" in reply:
    # This line is a hack, sometimes there is an OK within the buffer
    # Either get it or timeout - don't care which
    reply = waitReply(serial, 1, "OK")
    # Echo On
    serial.write("ATE1\r\n")
    wait(500)

    reply = waitReply(serial, 5, "OK")
    display(reply)
    # Does the modem support auto baud? Docs say yes, this command
    # says no :) NOTE Maybe only when baud is set to 0 do we get autobaud
    serial.write("AT+IPR=?\r\n")
    wait(500)

    reply = waitReply(serial, 5, "OK")
    display(reply)
    # We know UART can understand us at the present baud so
    # fix the baud we really want...
    serial.write("AT+IPR=" + str(TARGET_BAUD) + "\r\n")
    reply = waitReply(serial, 5, "OK")
    display(reply)

else:
    # Don't really know what to do - try rebooting
    # Shouldn't ever be here but cntrl-c during development
    # does weird stuff and "once" this helped.
    pass

for n in range(2):
    hardware.buzz_on()
    wait(1000)
    hardware.buzz_off()
    wait(300)
hardware.flash_led("white", True)

###############
# Setup Modem #
###############
# Sometimes we can get timeouts, just retry
# setting up the modem. The COMMANDS are within BootFunctions.py
# Basically - reduce search space from global bands to UK.
# We use roaming and want LTE CAT-M1
for cmd in COMMANDS:
    reply = "Timeout"
    while "Timeout" in reply:
        reply = waitReply(serial, 1, "OK")
        serial.write(cmd[0] + "\r\n")
        reply = waitReply(serial, cmd[1], cmd[2])
        display(reply)
    wait(25)

hardware.flash_led("green", True)

#############################
# Setup SIM7000 Custom Apps #
#############################
for ind, cmd in enumerate(TCP_COMMANDS):
    reply = waitReply(serial, 1, "OK")
    serial.write(cmd[0] + "\r\n")
    reply = waitReply(serial, cmd[1], cmd[2])
    display(reply)
    wait(25)

for n in range(2):
    hardware.buzz_on()
    wait(1000)
    hardware.buzz_off()
    wait(300)


hardware.flash_led("red", False)
hardware.flash_led("white", False)
hardware.flash_led("green", False)
hardware.stopTimer()
hardware.set_led("red", 0)
hardware.set_led("white", 0)
hardware.set_led("green", 0)