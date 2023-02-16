import network
import binascii
import utime as time
from Support.SupportFunctions import wait, display
from Config import WIFI_TIMEOUT, KN_NETWORKS, CLIENT_ID

#####################
# Simple WiFi class #
#####################
class WiFi:

    ########
    # init #
    ########
    def __init__(self):
        self.ssid = ''
        self.rssi = None
        self.sta_if = None

    ##############
    # disconnect #
    ##############
    def disconnect(self):
        self.sta_if.disconnect()
    #
    #
    ############
    # get RSSI #
    ############
    def getRSSI(self):

        available = self.sta_if.scan()
        available = self.sortNetworks(available)
        # ,_ for old ESP32
        if CLIENT_ID != b"246f284a6c94" and CLIENT_ID != b"bcddc2cfcb68":
            for i, (ssid, bssid, channel, rssi, stype, security, hidden) in enumerate(available):
                if self.ssid == ssid:
                    self.rssi = rssi
                    return rssi
            else:
                for i, (ssid, bssid, channel, rssi, stype, security, hidden,_) in enumerate(available):
                    if self.ssid == ssid:
                        self.rssi = rssi
                        return rssi               
        # If we get here then SSID isnt on list
        self.rssi = None
        return None


    ################
    # sortNetworks #
    ################
    def sortNetworks(self, available):
        for i in range(len(available)):
            available[i] = list(available[i])
            available[i][0] = available[i][0].decode('utf-8')
            available[i][1] = binascii.hexlify(available[i][1], '-').decode().upper()

        # Sort networks by signal strength RSSI so we try to connected to strongest first
        available = sorted(available, key=lambda x: x[3], reverse=True)

        return available

    ###########
    # connect #
    ###########
    def connect(self):
        
        # Start WiFi 
        connected = False

        display("Connecting WiFi")

        # Loop until we are connected - allows a known network to be found
        # even if not available yet
        while not connected:

            display("Resetting Interface")

            # Setup IF
            self.sta_if = network.WLAN(network.STA_IF)

            # Sometimes re-connects and saved info may cause problems
            self.sta_if.active(False)
            wait(2000)
            self.sta_if.active(True)

            # We need to know which one we used because no easy way of finding out when connected
            ssid_used = ''
            rssi_used = None

            # Scan
            display("Scanning for WiFi networks")
            available = self.sta_if.scan()

            # Decode and format the details
            available = self.sortNetworks(available)    

            # Check each SSID 
            display("Going through each network looking for known SSIDS")
            for i, v in enumerate(available):
                display(v)
                # one more value for older ESP32(ssid, bssid, channel, rssi, stype, security,_) = v
                if CLIENT_ID != b"246f284a6c94" and CLIENT_ID != b"bcddc2cfcb68":
                    (ssid, bssid, channel, rssi, stype, security) = v
                else:
                    (ssid, bssid, channel, rssi, stype, security, _) = v
                found = False
                
                # Is this SSID known to us?
                for i, (knSSID, PW) in enumerate(KN_NETWORKS):
                    
                    # If so, try it
                    if ssid == knSSID:
                        display("Found known SSID, trying:" + str(ssid))
                        self.sta_if.connect(ssid, PW)
                        ssid_used = ssid
                        rssi_used = rssi
                        
                        # We have a timeout to control loop
                        start = time.time()

                        # wait for timeout or a connection
                        display("Waiting for connection...")
                        while self.sta_if.isconnected() == False:
                            wait(1000)
                            display("...still waiting...")
                            # We shouldn't need this...but....
                            if time.time() > start + WIFI_TIMEOUT :
                                display("Timeout")
                                break
                        
                        # Could be here because of timeout or connection
                        if self.sta_if.isconnected() == True:
                            found = True # double loop exit
                            break

                        # NOTE may not need this but i think it cleans up stuff
                        self.sta_if.disconnect()

                # We need to break from double loop        
                if found: 
                    connected = True
                    break

            # For debug
            if connected:            
                display("Connected: " + str(ssid_used))
                print("Details:", self.sta_if.ifconfig())
            else:
                display("Looking for known WiFi networks")

            self.ssid = ssid_used
            self.rssi = rssi_used
            