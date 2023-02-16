from Config import *
from Support.DateTime import getDateTime
from Support.SupportFunctions import wait
from Support.GSMSupport import *
from machine import Pin, ADC

battery = ADC(Pin(35))
battery.atten(ADC.ATTN_11DB)
 

def getESPBattery():
    Vmax = 2450 # Attenuation takes max V from 0.95v to 2.45v
    Dmax = 4095
    # Something to do with voltage dividers / attenuation
    # and the fact that these batteries are 4.2v max (even though
    # they are 3.7v 18650s) 3.3 was found to be the correct multiplier
    mult = 3.3 

    t = getDateTime()

    # Average readings (they are only approx after all)
    vt = 0
    for i in range(50):
        vt += battery.read() * (Vmax / Dmax) * mult
        wait(10)
    v = int(vt / 50) / 1000

    status = "On Charge"
    if v >= BATTERY_FULL_LEVEL:
        status = "Full"
    elif v >= BATTERY_GOOD_LEVEL and v < BATTERY_FULL_LEVEL:
        status = "Good"
    elif v >= BATTERY_LOW_LEVEL and v < BATTERY_GOOD_LEVEL:
        status = "Poor"
    elif v > 1 and v < BATTERY_LOW_LEVEL:
        status = "Low - Needs Charging"

    # Connected via serial cable?
    # We get reading of 0.3v ish when plugged in
    if v < 1:
        v = "Plugged in"
    else:
        v = str(v)

    
    
    return str(t), v, status