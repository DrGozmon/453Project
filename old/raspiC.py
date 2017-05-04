# Publisher and Subscriber (Liz's RPi)

# ------------------------------------------------------
# ------------------ Description -----------------------
# ------------------------------------------------------

# Publish to (QoS == 2):
# - LightStatus
#    o "lightSensor" value >= "threshold" value
#      then the result is "TurnOn" otherwise "TurnOff"
#    o Only publish if result is different from most recent value on this topic
# - Status/RaspberryPiC

# Subscribe to (QoS == 2):
# - lightSensor (from the LDR)
# - threshold (from the potentiometer)
# - LightStatus (either TurnOff or TurnOn)

# Upon connection:
# - retain flag = true
# - publish "online" to Status/RaspberryPiC
# - create a lastwill message for Status/RaspberryPiC = "offline"

# ------------------------------------------------------
# ---------------------- Code --------------------------
# ------------------------------------------------------

# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt

lightSensor = 0
threshold = 0
LightStatus = ''

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print('Connected with result code ' + str(rc))

    # SUBSCRIPTIONS
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe('lightSensor', 2) # Set the QOS to 2
    client.subscribe('threshold', 2)   # Set the QOS to 2
    client.subscribe('LightStatus', 2) # Set the QOS to 2

    # Publish "online" to Status/RaspberryPiC
    client.publish(topic='Status/RaspberryPiC', payload='online', qos=2, retain=True)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print('Topic: ' + msg.topic + '\nMessage: ' + msg.payload.decode())

    # LightStatus publishing
    #  - "lightSensor" value >= "threshold" value
    #      then the result is "TurnOn" otherwise "TurnOff"
    #  - Only publish if result is different from most recent value on this topic
    if (msg.topic == 'lightSensor'):
        global lightSensor
        lightSensor = float(msg.payload.decode())
    elif (msg.topic == 'threshold'):
        global threshold
        threshold =float(msg.payload.decode())
    elif (msg.topic == 'LightStatus'):
        global LightStatus
        LightStatus =msg.payload.decode()
    else:
        print('Invalid topic: ' + msg.topic)

    result = 'TurnOff'
    if (lightSensor <= threshold):
        result = 'TurnOn'

    # Only publish the result if different than current value of LightStatus
    if (result != LightStatus):
        client.publish(topic='LightStatus', payload=result, qos=2, retain=True)

client = mqtt.Client(client_id="RaspiC", clean_session=False) # retain flag (clean_session) = false

# Create a lastwill message for Status/RaspberryPiC = "offline"
client.will_set(topic='Status/RaspberryPiC', payload='offline', qos=2, retain=True)
client.username_pw_set("RaspiC", password="passwordC")
client.on_connect = on_connect
client.on_message = on_message

# TODO: Connect to a remote broker, not localhost
client.connect('192.168.43.112', 1883, 5)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

# This takes care of the thread that handles the incoming messages
# Publishing only happens when a message is received
client.loop_forever()
