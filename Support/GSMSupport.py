#import gsm
import time
from Support.SupportFunctions import wait, display
from Config import *


def GSMConnect():
    return "Wifi"
    # Status
    connect = False
    operator = ""

    # TODO check if this is still needed
    wait(2000)
    status = gsm.status()[1]
    # If not started (am guessing a lost signal will cause
    # gsm to timeout, disconnect and therefore stop)
    # Therefore restart GSM
    if  status == "Not started":
        while gsm.status()[1] == "Not started":
            register()
            wait(5000)
        connect = True

    # If not connected (but GSM is started)
    if status != "Connected":
        display("Connecting")
        gsm.connect()
        start = time.time()

        # Wait until we are connected
        # Even if the connection timesout, keep looping
        # since we we are useless without connection
        while gsm.status()[1] != "Connected":

            # Unless we timeout in which case force a GSM restart
            if time.time() > start + REGISTER_TIMEOUT:
                start = time.time()
                register()
                connect = True
                operator = gsm.atcmd('AT+COPS?', printable=True).split()[2]
            
            # Arbitary time - just feel we ought to pause a little
            wait(5)

        display("Connected")

        # If we had to restart LTE modem signal this fact
        if connect == True:
            return operator
        return ""



def GSMDisconnect():
    return
    wait(2000)
    if gsm.status()[1] == "Connected":
        display("Disconnecting")
        gsm.disconnect()
        while gsm.status()[1] == "Connected":
            wait(5)
            
        display("Disconnected")

############
# register #
############
def register():
    return
    if GSM_DEBUG:
        gsm.debug(True)  # Uncomment this to see more logs, investigate issues, etc.
    gsm.start(tx=27, rx=26, apn=GSM_APN, user=GSM_USER, password=GSM_PASS, roaming=ROAM, wait=WAIT, connect=CONNECT)     