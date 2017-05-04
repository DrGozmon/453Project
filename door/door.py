# Publisher

# ------------------------------------------------------
# ------------------ Description -----------------------
# ------------------------------------------------------

# Publish to (QoS == 2):
# - the door topic
# - Status/RaspberryPiA
#    o Upon connection, publish "online" to this topic
#    o Lastwill message = "offline"

# Upon connection:
# - retain flag = true
# - publish "online" to Status/RaspberryPiA
# - create a lastwill message for Status/RaspberryPiA = "offline"

# ------------------------------------------------------
# ---------------------- Code --------------------------
# ------------------------------------------------------

# -*- coding: utf-8 -*-
import sys
import paho.mqtt.client as mqtt
from time import sleep
import datetime
from _thread import *
from gpiozero import MCP3008, LED

sys.path.append('/home/pi/453Project/utils')

import Constants

# Set the correct channel
LDR_CHANNEL = 0

door_sensor = ''
door_status = ''

# Authentication
CLIENT_ID = 'RaspiB'
PSWD = 'passwordB'

# The threshold difference we have to distinguish between the door
# being open or closed
THRESH = .05

# Set the amt of time to sleep between publishes
SLEEP = 2

# TODO Determine the number to scale the LDR with
SCALE = 2.1276595744681


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print('Connected with result code ' + str(rc))

    client.subscribe(Constants.DOOR_SENSOR_TOPIC, 2)   # Set the QOS to 2
    client.subscribe(Constants.DOOR_STATUS_TOPIC, 2)   # Set the QOS to 2


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print('Topic:' + msg.topic + '\nMessage: ' + msg.payload.decode())
    global door_sensor
    global door_status

    # Set the global variables corresponding to the topic's msg
    if msg.topic == Constants.DOOR_SENSOR_TOPIC:
        content = msg.payload.decode()
        l = content.split(',')
        door_sensor = float(l[1])
    if msg.topic == Constants.DOOR_STATUS_TOPIC:
        content = msg.payload.decode()
        l = content.split(',')
        door_status = l[1]
    else:
        print('Invalid topic: ' + msg.topic)


# Handles the publishing thread
def publisher_thread():
    # Set up the LDR
    ldr = MCP3008(channel=LDR_CHANNEL)


    filename = "/home/pi/453Project/door/data/doorData.txt"
    file = open(filename, 'a')

    # TODO Check Normalization of values
    while True:
        # lightSensor publishing (from the LDR)
        global door_sensor
        global door_status

        currentLDR = ldr.value * SCALE
#        if abs(door_sensor - currentLDR) >= THRESH:
            # Since difference is outside threshold, publish

        door_sensor = currentLDR
        print("Door Sensor is:  ", door_sensor)
        if door_sensor > THRESH:
            door_status = Constants.DOOR_OPEN
        else:
            door_status = Constants.DOOR_CLOSED

        # if door_status == Constants.DOOR_OPEN:
        #    door_status = Constants.DOOR_CLOSED
        # elif door_status == Constants.DOOR_CLOSED:
        #    door_status = Constants.DOOR_OPEN
        # else:
        #    door_status = "UNDEFINED"
        #    print("Invalid door status:" + door_status)
 
        currentTime = datetime.datetime.now()
        msg_sensor = str(currentTime) + ',' + str(door_sensor)
        print("Sending to broker: " + msg_sensor)

        data = str(door_sensor) + ',' + str(currentTime) + '\n'
        file.write(data)

        client.publish(topic=Constants.DOOR_SENSOR_TOPIC, payload=msg_sensor, qos=2, retain=True)

        msg_status = str(currentTime) + ',' + str(door_status)
        print("Sending to broker: " + msg_status)
        client.publish(topic=Constants.DOOR_STATUS_TOPIC, payload=msg_status, qos=2, retain=True)

        # Only query every X seconds
        sleep(SLEEP)

# Set up the client mosquitto connection
client = mqtt.Client(client_id=CLIENT_ID, clean_session=False)  # retain flag (clean_session) = false
client.username_pw_set(CLIENT_ID, password=PSWD)
client.on_connect = on_connect

print("Connecting to broker...")
client.connect(Constants.BROKER_IP, 1883, 5)

# Create a thread that handles the publishing of the data
start_new_thread(publisher_thread, ())

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

# This takes care of the thread that handles the incoming messages
client.loop_forever()
