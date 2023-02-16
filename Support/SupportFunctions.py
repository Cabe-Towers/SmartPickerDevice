from Config import BATTERY_LOW_LEVEL, DEBUG
from Support.ATCommands import getCSQ
import utime as time
#import gsm

########
# wait #
########
def wait(delay):
    start = time.ticks_ms()
    while time.ticks_ms() < start + delay:
        a = 23 ** 2

##############
# displayGPS #
##############
def displayGPS(data):
    if DEBUG:
        lat = data['LATITUDE']
        lon = data['LONGITUDE']
        fix = data['FIX_STATUS']
        gnss = data['GNSS_RUN_STATUS']
        pdop = data['PDOP_RATING']
        hdop = data['HDOP_RATING']
        vdop = data['VDOP_RATING']
        meandop = data['MEAN_DOP_RATING']
        error = data['ERROR']
        display("GNSS: " + gnss + " Fix: " + fix + " Latitude: " + lat + " Long: " + lon + " PDOP:" + pdop +
                " HDOP: " + hdop + " VDOP: " + vdop + " meanDOP " + meandop )
        display("CSQ: " + getCSQ())


###########
# display #
###########
def display(string):
    if DEBUG:
        print(string)