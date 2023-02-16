import time
import ujson as json
from machine import reset
from Support.umqtt.simple import MQTTClient
from Support.SupportFunctions import display
from Support.GSMSupport import GSMConnect, GSMDisconnect
from Config import *
from Support.DateTime import getDateTime

############
# MQTT_pub #
############
def MQTT_pub(topic, data = ""):
    if USE_MQTT:
        status = True
        # Add unique client_id
        data['CLIENT_ID'] = CLIENT_ID
        data_out=json.dumps(data)
        
        # TODO connect() failed with OSError 118 on one occasion
        # NOTE related to keepalive time - 99% sure this was sorted
        display("MQTT_connect")

        # Keep trying, noise and poor signal may cause problems
        # but LTE modem is definitely connected, although we will reboot
        # upon timeout (default about 3 minutes)
        start = time.time()
        mqtt_client = None
        while mqtt_client == None:
            mqtt_client = MQTT_connect()
            if time.time() > start + MQTT_CONNECTION_TIMEOUT:
                return False

        display("MQTT_send")
        mqtt_client.publish(topic, data_out)

        display("MQTT_disconnect")
        mqtt_client.disconnect()

        return status
  

################
# MQTT_connect #
################
def MQTT_connect():
 
    mqtt_client = MQTTClient(keepalive=MQTT_KEEPALIVE, ssl=False, client_id=CLIENT_ID, server=MQTT_SERVER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASS)

    try:
        mqtt_client.connect()
        return mqtt_client
    except  Exception as e:
        display("MQTT Exception:" + str(e))
        del mqtt_client
        # We will run out of memory if we don't do something about this
        if "ENOBUFS" in str(e):
            reset()

    return None

#
#
########################
# sendConnectionStatus #
########################
def sendConnectionStatus(connectionType = "Reconnect", operator=""):
    t = getDateTime()
    data = {'Time': str(t), 'Type': connectionType, 'Operator': operator}
    MQTT_pub(MQTT_CONNECT_TOPIC, data)