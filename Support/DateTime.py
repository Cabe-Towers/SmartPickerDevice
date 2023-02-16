from machine import RTC
import utime
from Config import CLIENT_ID, TIMEZONE
if CLIENT_ID != b"246f284a6c94" and CLIENT_ID != b"bcddc2cfcb68":
    import ntptime

rtc = RTC()

###########
# setTime #
###########
# https://loboris.eu/forum/showthread.php?tid=12
def setTime(ntp_server):
    # new ESP32
    if CLIENT_ID != b"246f284a6c94" and CLIENT_ID != b"bcddc2cfcb68":
        ntptime.settime()
    else:
        # old ESP32
        rtc.ntp_sync(server=ntp_server, tz=TIMEZONE)  
        tmo = 100
        while not rtc.synced():
            utime.sleep_ms(100)
            tmo -= 1
            if tmo == 0:
                break
    
###############
# getDateTime #
###############
def getDateTime():
    if CLIENT_ID != b"246f284a6c94" and CLIENT_ID != b"bcddc2cfcb68":
        return utime.localtime(utime.time() + 3600)
    else:
        return rtc.now() # get date and time