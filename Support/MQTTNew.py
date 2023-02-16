import time
import ujson as json
from machine import reset
from Support.umqtt.simple import MQTTClient
from Support.SupportFunctions import display

from Config import *
from Support.DateTime import getDateTime

import gc
gc.collect()

class MQTTSimple:

    def __init__(self):
        self.client = None
        self.latest = 0
        self.previous = 0
        self.state = ""
        self.previousState = ""
        self.method = ""
        self.connect_and_subscribe()

    def sub_cb(self, topic, msg):
        msg = json.loads(msg.decode())
        self.latest = int(msg['epoch'])
        self.previousState = self.state
        self.state = str(msg['states']['STD_v2_'+ CLIENT_ID.decode()])
        self.method = str(msg['method'])


    def check_msg(self):
        r = self.client.check_msg()
        if self.latest > self.previous and self.method == 'update_orders':
            return True
        else: 
            return False

    def connect_and_subscribe(self):
        self.client = MQTTClient(keepalive=MQTT_KEEPALIVE, ssl=False, client_id=CLIENT_ID, server=MQTT_SERVER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASS)
        self.client.set_callback(self.sub_cb)
        self.client.connect()
        self.client.subscribe(MQTT_CALLBACK_TOPIC)
    
    ############
    # MQTT_pub #
    ############
    def MQTT_pub(self, topic, data = ""):
        # Add unique client_id
        data['CLIENT_ID'] = CLIENT_ID
        data_out=json.dumps(data)
        display("MQTT_send " + str(topic))
        try:
            self.client.publish(topic, data_out)
            return True
        except:
            return False
        



