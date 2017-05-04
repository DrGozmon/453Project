# Subscriber

# ------------------------------------------------------
# ------------------ Description -----------------------
# ------------------------------------------------------

# Subscribe to (QoS == 2):
# - lightSensor
# - threshold
# - LightStatus
# - Status/RaspberryPiA
# - Status/RaspberryPiC

# ALSO: keep record of when LED1 (see raspiB.py) was turned off and on

# ------------------------------------------------------
# ---------------------- Code --------------------------
# ------------------------------------------------------

import sys
import paho.mqtt.client as mqtt
import datetime
import os

lightSensor = ''
threshold = ''
LightStatus = ''
rpiA = ''
rpiC = ''
led1 = 'Off'

if len(sys.argv) != 2:
    print('Usage: python3 toggle.py <MosquittoServerIP>')
    exit()

serverIP = sys.argv[1]

fout = open('./laptop2.log', 'w')
ledout = open('./ledout.log', 'w')


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    output = 'Connected with result code ' + str(rc) + '\n'
    print(output)
    fout.write(output)

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe('lightSensor', qos=2)         # Set the QOS to 2
    client.subscribe('threshold', qos=2)           # Set the QOS to 2
    client.subscribe('LightStatus', qos=2)         # Set the QOS to 2
    client.subscribe('Status/RaspberryPiA', qos=2) # Set the QOS to 2
    client.subscribe('Status/RaspberryPiC', qos=2) # Set the QOS to 2


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    s = 'Topic: ' + msg.topic
    s += '\n   Message: ' + msg.payload.decode()
    s += '\n   TimeStamp: ' + str(datetime.datetime.now().time())

    print(s + '\n')
    fout.write(s + '\n')

    global lightSensor
    global threshold
    global LightStatus
    global rpiA
    global rpiC

    # Check whether LED1 is on/off here
    # Only time LED1 status changes is if the message is from the
    # LightStatus or Status/RaspberryPiC topics
    # if LightStatus == 'TurnOn' && Status/RaspberryPiC == 'online', 'On'
    # else result = 'Off'
    global led1
    change = 0
    led1 = ''
    if msg.topic == 'LightStatus':
        if msg.payload.decode() != LightStatus:
            led1 = msg.payload.decode()
            change = 1
    elif msg.topic == 'Status/RaspberryPiC':
        if msg.payload.decode() == 'online' and LightStatus == 'TurnOn':
            led1 = 'TurnOn'
            change = 1
        elif msg.payload.decode() == 'offline' and LightStatus != 'TurnOff':
            led1 = 'TurnOff'
            change = 1

    if change == 1:
        s = '** LED1 Changed:'
        s += '\n   Status: ' + led1
        s += '\n   TimeStamp: ' + str(datetime.datetime.now().time())

        print(s + '\n')
        fout.write(s + '\n')
        ledout.write(s + '\n')

    if (msg.topic == 'lightSensor'):
        lightSensor = msg.payload.decode()
    elif (msg.topic == 'threshold'):
        threshold = msg.payload.decode()
    elif (msg.topic == 'LightStatus'):
        LightStatus = msg.payload.decode()
    elif (msg.topic == 'Status/RaspberryPiA'):
        rpiA = msg.payload.decode()
    elif (msg.topic == 'Status/RaspberryPiC'):
        rpiC = msg.payload.decode()
    else:
        output = 'Invalid topic: ' + msg.topic
        print(output + '\n')
        fout.write(output + '\n')

client = mqtt.Client()

client.username_pw_set("Laptop", password="passwordD")
client.on_connect = on_connect
client.on_message = on_message

client.connect(serverIP, 1883, 5)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
