# Publisher and Subscriber (Alex's RPi)

# ------------------------------------------------------
# ------------------ Description -----------------------
# ------------------------------------------------------

# Publish to (QoS == 2):
# - lightSensor (from the LDR)
# - threshold (from the potentiometer)
# - Status/RaspberryPiA
#    o Upon connection, publish "online" to this topic
#    o Lastwill message = "offline"

# Subscribe to (QoS == 2):
# - lightSensor
# - threshold

# Upon connection:
# - retain flag = true
# - publish "online" to Status/RaspberryPiA
# - create a lastwill message for Status/RaspberryPiA = "offline"

# ------------------------------------------------------
# ---------------------- Code --------------------------
# ------------------------------------------------------

# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
from time import sleep
from _thread import *
from gpiozero import MCP3008, LED

# TODO Set the correct channels
POT_CHANNEL = 0
LDR_CHANNEL = 1

# The threshold difference we will allow in differing POT and LDR values
# Probably should use two different thresholds, one for LDR and one for
# pot.  They have different ranges.
THRESH = .05
# The number to scale the LDR with
SCALE = 2.1276595744681

lightSensor = 0
threshold = 0

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print('Connected with result code ' + str(rc))

    # SUBSCRIPTIONS
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe('lightSensor', 2) # Set the QOS to 2
    client.subscribe('threshold', 2)   # Set the QOS to 2

    # Publish "online" to Status/RaspberryPiA
    client.publish(topic='Status/RaspberryPiA', payload='online', qos=2, retain=True)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print('Topic:' + msg.topic + '\nMessage: ' + msg.payload.decode())
    global lightSensor
    global threshold
    # Set the global variables corresponding to the topic's msg
    if (msg.topic == 'lightSensor'):
        lightSensor = float(msg.payload.decode())
    elif (msg.topic == 'threshold'):
        threshold = float(msg.payload.decode())
    else:
        print('Invalid topic: ' + msg.topic)

# Handles the publishing thread
def publisher_thread():
    # Set up the LDR and potentiometer
    ldr = MCP3008(channel=LDR_CHANNEL)
    pot = MCP3008(channel=POT_CHANNEL)

    # TODO Check Normalization of values
    while (True):
        # lightSensor publishing (from the LDR)
        global lightSensor
        currentLDR = ldr.value * SCALE
        if (abs(lightSensor - currentLDR) >= THRESH):
            # Since difference is outside threshold, publish
            lightSensor = currentLDR
            client.publish(topic='lightSensor', payload=lightSensor, qos=2, retain=True)

        # threshold publishing (from the potentiometer)
        global threshold
        currentPOT = pot.value
        if (abs(threshold - currentPOT) >= THRESH):
            # Since difference is outside threshold, publish
            threshold = currentPOT
            client.publish(topic='threshold', payload=threshold, qos=2, retain=True)

        # Only query every 100 ms
        sleep(0.10)

# Set up the client mosquitto connection
client = mqtt.Client(client_id="RaspiA", clean_session=False) # retain flag (clean_session) = false

# Create a lastwill message for Status/RaspberryPiA = "offline"
client.will_set(topic='Status/RaspberryPiA', payload='offline', qos=2, retain=True)
client.username_pw_set("RaspiA", password="passwordA")
client.on_connect = on_connect
client.on_message = on_message

# TODO: Connect to a remote broker, not localhost
print("Connecting to broker...")
client.connect('192.168.43.112', 1883, 5)

# Create a thread that handles the publishing of the data
start_new_thread(publisher_thread, ())

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

# This takes care of the thread that handles the incoming messages
client.loop_forever()
