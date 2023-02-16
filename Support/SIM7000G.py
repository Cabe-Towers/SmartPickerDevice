# Andy modules
from Support.SupportFunctions import wait, displayGPS, display
from Support.ATCommands import getCSQ
from Support.BootFunctions import *
from Support.gpsFormat import gpsToDict
from Support.battery import  getESPBattery
from Config import *
from Support.DateTime import setTime, getDateTime
from Support.WiFi import WiFi
from Support.MQTTNew import MQTTSimple

# Other modules
#import uwebsockets.client
#from Support.umqtt.simple import MQTTClient

# MicroPython modules
import ujson as json
from machine import UART, reset, Pin, PWM
import machine

# Standard modules
import socket
import utime as time
import sys

############
# SIM7000G #
############ 
class SIM7000G:
    """ Interface with SIM7000G GPS and LTE Module. """
    def __init__(self, address="wss://lcas.lincoln.ac.uk/car/ws", user_name="picker02",
                 update_orders_cb = None):
        self.address = address
        self.user_name = user_name
        self.update_orders_cb = update_orders_cb
        self.registered = False
        self.lastMessage = 0
        self.batteryStatus = ""
        self.timer = machine.Timer(1)
        # Power on the GSM module
        self.GSM_PWR = machine.Pin(4, machine.Pin.OUT)
        self.GSM_PWR.value(1)
        wait(300)
        self.GSM_PWR.value(0)
        self.gpsD = gpsToDict('')

        # Green button led
        self.green_led = machine.Pin(33, machine.Pin.OUT)
        self.green_led.value(0)

        LED = machine.Pin(12, machine.Pin.OUT)
        LED.value(1)

        # Set serial port for reading GPS
        self.serial = UART(1,baudrate=115200, bits=8, parity=None, stop=1, rx=26, tx=27)

        # Connect or re-connect
        self.wifi = WiFi()
        self.wifi.connect()

        display("Setting clock using NTP")
        setTime(TIME_SERVER)
        display(getDateTime())

        self.startTimer()

        # Is MQTT down?
        down = True
        while down:
            try:
                display("Connecting to MQTT...")
                self.MQTTClient = MQTTSimple()
                down = False
                
            except:
                wait(1000)

    ##############
    # startTimer #
    ##############
    def startTimer(self):
        p = GPS_TIMER * 1000
        self.timer.init(period=p, mode=machine.Timer.PERIODIC, callback=self.check_for_updates)

    #############
    # stopTimer #
    #############
    def stopTimer(self):
        self.timer.deinit()

    ########
    # send #
    ########
    def send(self, message):
        display("Message: " + message)
        while not self.MQTTClient.MQTT_pub(MQTT_GPS_TOPIC, message):
            self.wifi.reconnect()


    ###########
    # recieve #
    ###########
    def recieve(self):
        #with uwebsockets.client.connect(self.address) as websocket:
        #    return websocket.recv()
        # TODO what is the receive message? 
        return "Receive Message"

    ###########
    # initGPS #
    ###########
    def initGPS(self):
        
        for ind, cmd in enumerate(TCP_COMMANDS):
            reply = waitReply(self.serial, 1, "OK")
            self.serial.write(cmd[0] + "\r\n")
            reply = waitReply(self.serial, cmd[1], cmd[2])

            display(reply)
            wait(25)

        display("Attempting to establish GPS signal.")
        # Get positioning data
        # Can take 50 tries to get a fixed position
        found = False
        for i in range(0,200):

            wait(500)

            # Get GPS info
            self.serial.write('AT+CGNSINF' + "\r\n")
            raw = waitReply(self.serial, 10, "OK")  # TODO check if this is the GPS timeout

            # Sometimes when on serial cable uploading files causes error / chip needs resetting
            try:
                print("raw[1]", raw[1])
            except IndexError:
                reset()
            wait(100)

            # Make dictionary
            self.gpsD = gpsToDict(raw[1])
            self.gpsD['CSQ'] = getCSQ()
            self.gpsD['user'] = "STD_v2_" + CLIENT_ID.decode('utf-8')

            # Output information
            displayGPS(self.gpsD)

            # Publish
            operator = self.MQTTClient.MQTT_pub(MQTT_GPS_TOPIC, self.gpsD)

            # If we have good GPS coords then break
            try:
                if self.gpsD["LATITUDE"] != "" and self.gpsD["LONGITUDE"] != "" and int(self.gpsD["GNSS_SATELITES_IN_VIEW"]) >= 4 and i > 5:
                    found = True
                    break
            except:
                # This will be caused by empty string, ignore
                pass
        # Perhaps the chip gets confused and GPS isn't working - had this once
        if not found:
            reset()

        if self.gpsD['GNSS_RUN_STATUS'] == "1" and self.gpsD['FIX_STATUS'] == "1" and not self.gpsD['ERROR']:
                # Then GPS connected and values recieved
                return 1
        
    #############
    # addFields #
    #############
    def addFields(self):
        self.gpsD['CSQ'] = getCSQ()
        self.gpsD['user'] = "STD_v2_" + CLIENT_ID.decode('utf-8')
 
    ############
    # register #
    ############
    def registerBack(self):
        display("Registering with backend")
        data = {'method':'register', 'admin': False, 'user': self.user_name}
        while not self.MQTTClient.MQTT_pub(MQTT_REGISTER_TOPIC, data):
            self.reconnectWiFi()
        self.registered = True
        # Buzzer
        buzz = PWM(Pin(12, Pin.OUT))
        buzz.init(freq=5000, duty=50)
        wait(3000)
        buzz.deinit()
        # for n in range(100):
        #     wait(1000)
        #     data = {'method':'get_states', 'user': self.user_name}
        #     while not self.MQTTClient.MQTT_pub(MQTT_METHOD_TOPIC, data):
        #         self.reconnectWiFi()


    #################
    # reconnectWiFi #
    #################
    def reconnectWiFi(self):
        # disconnecting and reconnecting will run out of memory sometimes !
        # don't know why (LoBo Micropython issue?)
        del self.wifi
        self.wifi = WiFi()
        #self.wifi.disconnect()
        display("Reconnecting..................")
        self.wifi.connect()
        self.MQTTClient = MQTTSimple()
        display("RETRY WiFI count:" + str(self.retryCount))

    ###############
    # sendBattery #
    ###############
    def sendBattery(self):
        t, v, s = getESPBattery()
        if v != None:
            self.batteryStatus = s
            data = {"CLIENT_ID" : CLIENT_ID, "Time": t, "Voltage" : v, "Status":s, "user": self.user_name}
            while not self.MQTTClient.MQTT_pub(MQTT_BATTERY_TOPIC, data):
                self.reconnectWiFi()

    ##############
    # call_robot #
    ##############
    def call_robot(self):
        display("Call")
        data = {'method':'call', 'user': self.user_name}
        while not self.MQTTClient.MQTT_pub(MQTT_METHOD_TOPIC, data):
            self.reconnectWiFi()

    #
    ################
    # cancel_robot #
    ################
    def cancel_robot(self):
        display("Cancel")
        data = {'method':'cancel', 'user': self.user_name}
        while not self.MQTTClient.MQTT_pub(MQTT_METHOD_TOPIC, data):
            self.reconnectWiFi()        

    ##############
    # set_loaded #
    ##############
    def set_loaded(self):
        display("Loaded")
        #data = {'method':'car_load', 'user': self.user_name}
        data = {'method':'set_state', 'user': self.user_name, 'state': 'LOADED'}
        while not self.MQTTClient.MQTT_pub(MQTT_METHOD_TOPIC, data):
            self.reconnectWiFi()       
 
    ############
    # set_init #
    ############
    def set_init(self):
        #data = {'method':'car_init', 'user': self.user_name}
        data = {'method':'set_state', 'user': self.user_name, 'state': 'INIT'}
        while not self.MQTTClient.MQTT_pub(MQTT_METHOD_TOPIC, data):
            self.reconnectWiFi()

    ############
    # send_gps #
    ############
    def send_gps(self, ts=time.time()):
        self.getGPS()
        while not self.MQTTClient.MQTT_pub(MQTT_GPS_TOPIC, self.gpsD):
            self.reconnectWiFi()
    #
    #
    #####################
    # check_for_updates #
    #####################
    def check_for_updates(self,_):
        """ CALLBACK """
        if self.registered:
            display("Getting GPS Coords")
            try:
                self.send_gps()
                self.sendBattery()
                display("Checking for updates to state...")
                if self.MQTTClient.check_msg() == True:
                    if self.MQTTClient.latest > self.lastMessage and self.MQTTClient.method == "update_orders" and self.MQTTClient.previousState != self.MQTTClient.state:
                        display("New state: " + str(self.MQTTClient.state))
                        self.update_orders_cb(self.MQTTClient.state)
                        self.lastMessage = self.MQTTClient.latest
            except Exception as e:
                display("Exception: " + str(e))
                self.reconnectWiFi()

    ############
    # shutdown #
    ############
    def shutdown(self):

        display("Shutting Down.")
        self.registerd = False
        
    ##########
    # getGPS #
    ##########
    def getGPS(self):

        self.gpsD['GNSS_RUN_STATUS'] = "0"
        self.gpsD['FIX_STATUS'] = "0"
        while self.gpsD['GNSS_RUN_STATUS'] != "1" and self.gpsD['FIX_STATUS'] != "1":

            # Get positioning data
            self.serial.write('AT+CGNSINF' + "\r\n")
            raw = waitReply(self.serial, 10, "OK")
            
            # Output information
            self.gpsD = gpsToDict(raw[1])
            self.addFields()
            displayGPS(self.gpsD)
