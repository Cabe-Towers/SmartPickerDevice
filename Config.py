import machine
import ubinascii

# Displays whats going on
DEBUG = True

# Displays debug info when connecting to mobile
GSM_DEBUG = False

# False means send via websockets
USE_MQTT = True

# TIME - RTC is updated upon boot
TIME_SERVER = "uk.pool.ntp.org"
TIMEZONE = "GMT0BST,M3.5.0/1,M10.5.0"

# A check is done on GPS date - just sanity, can be expanded
# TODO this needs changing so that it checks time within x minutes of RTC
MIN_YEAR = 1970
MAX_YEAR = 2030
# CEP50 is 2.5m and expected accuracy is < 5m which makes ideal or excellent viable
# CEP75 or CEP97 is not known. Good would mean 50% are within <12.5m, excellent <5m, ideal <2.5m
ACCEPTED_DOPS = ["ideal", "excellent", "good"]

# Need to still work this out since SIM7000 expects input from solar panel
# I beleive 4.2 is 100% for a 18560 3.7v battery 
BATTERY_LOW_LEVEL = 3.5 # leave as 3.2 for shemnz batteries
BATTERY_GOOD_LEVEL = 3.6
BATTERY_FULL_LEVEL = 3.9

# Connection to mobile operator
ROAM = True # currently using KPN from Netherlands, so need to roam
WAIT = True # Leave True
CONNECT = False # This is initial connection status - leave False

# GPS Periodic Timer - send data every x seconds
GPS_TIMER = 5

# APN credentials
GSM_APN = 'fast.m2m' 
GSM_USER = ''
GSM_PASS = '' 
# NOTE 1st connection with a 7000G means it has to scan all the channels in the world
# Therefore it can take hours to make a connection
# Once connected it stores info about the connection and tries that connection first
# so that it connects faster next time !!!!!!!!!!!!!
# PAINFUL LESSON LEARNT
# https://community.hologram.io/t/sim7000g-botletics-network-status-2-not-registered-searching/3533/11
REGISTER_TIMEOUT = 120 # seconds

# MQTT
MQTT_SERVER = b'mqtt.lcas.group' #'mqtt.lar.lincoln.ac.uk' #b'194.80.55.245' #b"test.mosquitto.org"
MQTT_PORT = 1883 # 8097 # LAR port
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
MQTT_USER = b'andy' #b"andy"
MQTT_PASS = b'!qswd3288!S' #b"dasda"
MQTT_GPS_TOPIC = b'trolley/gps'
MQTT_REGISTER_TOPIC = b'trolley/register'
MQTT_METHOD_TOPIC = b'trolley/method'
MQTT_BATTERY_TOPIC = b'trolley/battery'
MQTT_CALLBACK_TOPIC = b'trolley/status'
MQTT_CONNECT_TOPIC = b'trolley/connection'

# Must be a fair bit longer than either timer value - 250 should be fine
MQTT_KEEPALIVE = 250

# If we can't connect remake LTE connection
MQTT_CONNECTION_TIMEOUT = 20
#
# When looking for and connecting to a network (seconds)
WIFI_TIMEOUT = 15

# SSID, PWD/KEY
KN_NETWORKS = [
    ["Xiaomi 12", "1234567890"],
    ["unifi-lcas", "cogxxgoc"],
    #['Sagarobotics_T2', ''],
    #['RUT240_E554', ''],
    #['RUT240_A05E', ''],
    #['lcas_network', ''],
    #['lcas_network', ''],
    ["saga_robotics","visitKent"],
    ['SagaRobotics_guest', 'Sagar0botics'],
    ["BTHub6-63S6", "NqGftQKXigA6"]
]
