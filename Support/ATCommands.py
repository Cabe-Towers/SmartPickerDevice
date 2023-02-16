#import gsm


# received signal strength indication
# Signal Quality Report
def getCSQ():
    return "Wifi"
    try:
        err = False

        # Save status
        stat = gsm.status()

        # Can't issue AT commands if connected
        if stat[1] != 'Idle':
            gsm.disconnect()

        # should get ..+CSQ: 30,99....OK..
        raw = gsm.atcmd('AT+CSQ', printable=True)
        parts = raw.split(':')
        # should have 30,99....OK..
        csq = parts[1].split(',')
        # should have 30
        csq = int(csq[0].strip())
        
        # No idea what else it could be for an error
        # Serial stuff can get corrupted so this is really just a
        # sanity test
        value = ""
        if not ("..OK.." in parts[1]):
            value = "Error"

        if csq == 0:
            value = "-115 dBm or less"
        elif csq < 31:
            value = str(-112 + csq) + " dBm"
        elif csq == 31:
            value = "-52 dBm or greater"
        else:
            value = "Error"

    # TODO did this reconnect cause this?
    # Traceback (most recent call last):
    #   File "main.py", line 134, in <module>
    #   File "main.py", line 26, in __init__
    #   File "Support/SIM7000G.py", line 148, in initGPS
    #   File "Support/MQTTSupport.py", line 18, in MQTT_pub
    #   File "Support/MQTTSupport.py", line 31, in MQTT_connect
    #   File "Support/umqtt/simple.py", line 68, in connect
    # OSError: 118
        # Reconnect if needed
        #if stat[1] != 'Idle':
        #    gsm.connect() 

        return value

    except: 
        return "Error"