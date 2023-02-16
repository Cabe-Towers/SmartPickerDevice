# Andy Perrett (PER18684092)
# For Smart Trolly / Call-a-Robot
# ONLY used to support boot.py

# NOTE nothing needs setting in here

import utime as time
import sys
from Config import *
from Support.SupportFunctions import wait, display


CMD_LINEBREAK = b'\r\n'
BAUD_RATES = [300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200,
    230400, 921600, 2000000, 2900000, 3000000, 3200000, 3686400, 4000000]
RESPONSES = ["Rdy", "Ready", "OK", "rdy", "ready", "ok", "ERROR", "Error"]

# Works with any baud BUT LoBo MicroPython prefers 115200 - leave alone!
TARGET_BAUD = 115200 

# Setup Modem
COMMANDS = [
    ["ATZ", 30, "OK"],
    #["ATE0", 40, "OK"],
    ##["AT+CBANDCFG?", 30, "OK"],
    ##["AT+CBANDCFG=\"CAT-M\",1,3,8,20", 360, "OK"],
    ##["AT+CBANDCFG=\"NB-IOT\",1,3,8,20", 360, "OK"],
    ##["AT+CPIN?", 30, "OK"],
    ##["AT+CIPSHUT", 100, "OK"],
    ["AT+CFUN=1", 30, "OK"], 
    ##["AT+CREG?", 30, "OK"],
    #["AT+CREG=1", 30, "OK"],
    #["AT+CEREG?", 30, "OK"],
    #["AT+CEREG=1", 30, "OK"],
    #["AT+CGREG?", 30, "OK"],
    #["AT+CGREG=1", 30, "OK"],
    #["AT+CNMI=0,0,0,0,0", 30, "OK"],
    #["AT+CGATT=1", 75, "OK"],
    #["AT+CLTS=1", 30, "OK"],
    ##["AT+CNMP=38", 30, "OK"],
    ##["AT+CMNB=1", 30, "OK"],
    #["AT+CNBS=1", 30, "OK"],
    ##["AT+CNSMOD=?", 2000, "OK"],
    ##["AT+CNSMOD?", 2000, "OK"],
    #["AT+CNSMOD=1", 2000, "OK"],
    ["AT+GSV", 30, "OK"],
    ["AT+CSQ", 30, "OK"],
    ##["AT+CGNAPN=?", 2000, "OK"],
    ##["AT+CGNAPN", 2000, "OK"],
    ##["AT+COPS?", 2000, "OK"],
    #["AT+COPS=?", 2000, "OK"],
    #["AT+CPOL?", 2000, "OK"],
    #["AT+COPS=0,\"O2 - UK\", 7", 120, "OK"], # 
    ##["AT+CCLK?", 30, "OK"],
    ##["AT+CPSI?", 30, "OK"],
    #["AT+CSTT=\"" + GSM_APN + "\",\"" + GSM_USER + "\",\"" + GSM_PASS + "\"", 30, "OK"],
    #["AT+CIICR", 30, "OK"],
    #["AT+CGDCONT=?", 2000, "OK"],
    #["AT+CGDCONT=1,\"IP\",\"" + GSM_APN + "\"", 10, "OK"],
    #["AT+S7=10", 100, "OK"],
    ##["AT+CNSMOD?", 100, "OK"],
    ##["AT+CIPSTATUS", 100, "OK"],
    #["ATD*99***1#", 20, "CONNECT"],
    #["AT+CGACT?", 150, "OK"],
    #["AT+CGACT=1,1", 150, "OK"],
    ##['AT+CGPADDR', 2000, "OK"],
    #["AT+CDNSCFG?", 100, "OK"],
    #["AT+CIFSR", 100, "OK"],
    #["AT+CGDATA=\"PPP\",1", 100, "CONNECT"],
    #["AT+CPING=\"www.google.com\",1", 100, "OK"],
]

# SIM7000 custom Apps
TCP_COMMANDS = [
    #["AT+CGATT?", 100, "OK"],
    #["AT+CNACT=1,\"" + GSM_APN + "\"", 10, "OK"],
    #["AT+CNACT?", 10, "OK"],
    #["AT+SMSTATE?", 10, "OK"],
    #["AT+CIPMODE=1", 100, "OK"],
    #["AT+CSTT=\"" + GSM_APN + "\"", 100, "OK"],
    #["AT+CIICR", 100, "OK"],
    #["AT+CIPSTATUS=?", 30, "OK"],
    #["AT+CIFSR", 10, "Timeout"],
    #["AT+CIPPING=\"8.8.8.8\"", 100, "OK"],
    #["AT+CIPPING=\"www.google.co.uk\"", 100, "OK"],
    #['AT+CDNSCFG?', 30, "OK"],
    # GPS power
    ["AT+CGNSPWR=1", 10, "OK"],
    ["AT+SGPIO=0,4,1,1", 10, "OK"],
]

# TODO WOuld be nice to make MQTT work reliably so we can send
# Boot up logs - intermittent timeouts and simply doesn't work well
MQTT_COMMANDS = [
    ["AT+SMCONF=\"CLIENTID\",\"12345\"", 60, "OK"],
    ["AT+SMCONF=\"URL\",194.80.55.245,8097", 60, "OK"],
    ["AT+SMCONF=\"KEEPTIME\",60", 60, "OK"],
    ["AT+SMCONF=\"CLEANSS\",0", 60, "OK"],
    ["AT+SMCONF=\"USERNAME\",\"andy\"", 60, "OK"],
    ["AT+SMCONF=\"PASSWORD\",\"**********\"", 60, "OK"],
    ["AT+SMCONF=\"QOS\",0", 60, "OK"],
    ["AT+SMCONF=\"TOPIC\",\"trolley/gps\"", 60, "OK"],
    ["AT+SMCONF=\"MESSAGE\",\"Boot Complete\"", 60, "OK"],
    ["AT+SMCONF=\"RETAIN\",0", 60, "OK"],
    ["AT+SMCONN", 60, "OK"],
    ["AT+SMSUB=\"trolley/gps\",1", 60, "OK"],
    ["AT+SMPUB=\"trolley/gps\",13,1,1", 120, "OK"],
    ["AT+SMUNSUB=\"trolley/gps\"", 60, "OK"],
    ["AT+SMDISC", 60, "OK"],
    ["AT+CNACT=0,\"" + GSM_APN + "\"", 60, "OK"],
]



################
# findBaudRate #
################
# Should return ["AT", "OK"] if it was successful
def findBaudRate(gsm):
    # find baud rate
    done = False
    reply = []
    for baud in BAUD_RATES:
        display("Trying baud: " + str(baud))
        # Init UART - timeout and char_timeout are guesses, too low and things fail
        # buffers, not sure but cmd line buffer can be MAX 559 characters. I think buffer relates to a "line"
        # and sometimes some responses may need many lines?
        gsm.init(baudrate=baud, bits=8, parity=None, stop=1, rx=26, tx=27)
        wait(5)
        startTime = time.time()
        # Time out is 1 second - no idea what to set this to really - 1 sec works though
        while time.time() < startTime + 1:
            # Issue AT cms and we are looking for a known response
            gsm.write("AT\r\n")
            # Maybe don't need to wait, but why not....
            wait(5)
            # Ideally we should check the number of characters in buffer BUT that value isn't always correct
            # Far easier to presume we have a full line already there
            a = gsm.readline()
            if a != None:
                # Even if we have data that is a good response sometimes it can't be converted (Why?)
                try:
                    a = a.decode('utf-8').strip()
                except UnicodeError:
                    #print("Got something back - couldn't be decoded")
                    # Ignore this response - its no good to us
                    a = None
            if a != None:
                # Got error reponse once - can't reproduce
                if a == "ERROR":
                    break
                reply.append(a)
                # Getting an "OK" respose will normally mean we have found the correct baud
                # NOTE but not always! Keep collecting reponses, we'll check them later
                if a in RESPONSES:
                    display("Baud: " + str(baud))
                    display("Response: " + str(a))
                    done = True
                    # Seems to make the modem more reliable - maybe helps sync flow control?
                    #gsm.sendbreak()
                    break
        # We appear to be able to send a command and get a reasonable response
        if done:
            reply = [x for x in reply if x]
            return reply

    # Timeout - no more baud rates to try
    reply = [x for x in reply if x]
    return reply  


#############
# waitReply #
#############
def waitReply(simcom, timeout=10, response="OK", actResponse = True):
    reply = list()
    startTime = time.time()  
    while time.time() < startTime + timeout:
        # Sometimes a response can't be decoded and will cause exception
        try:
            n = simcom.any()
            if n != 0:
                line = simcom.readline()
                line = line.decode().strip()
                reply.append(line)
                # NOTE the first "OK" response may be left over from previous command
                if response in line and actResponse:
                    reply = [x for x in reply if x]
                    return reply
            else:
                wait(5)
        except KeyboardInterrupt:
            # quit
            sys.exit()
        except:
            reply.append("Error")
    reply.append("Timeout")
    reply = [x for x in reply if x]
    return reply