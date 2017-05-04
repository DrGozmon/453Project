# Subscriber (Mike's RPi)

# ------------------------------------------------------
# ------------------ Description -----------------------
# ------------------------------------------------------

# Subscribe to (QoS == 2):
# - LightStatus (either TurnOff or TurnOn)
# - Status/RaspberryPiA
# - Status/RaspberryPiC

# LED's:
# - LED1 -- "LightStatus" topic
#   o if no value yet -- keep off the light
#   o "TurnOff" -- turn off the light
#   o "TurnOn" -- turn on the light
# - LED2 -- "Status/RaspberryPiA" topic
#   o "offline" -- turn off the light
#   o "online" -- turn on the light
# - LED3 -- "Status/RaspberryPiC" topic
#   o "offline" -- turn off the light (for LED1 AND LED3)
#   o "online" -- turn on the light

# ------------------------------------------------------
# ---------------------- Code --------------------------
# ------------------------------------------------------

import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
from gpiozero import LED

# TODO: Change these to the correct pin numbers
global LED1
LED1 = LED(21)
global LED2
LED2 = LED(26)
global LED3
LED3 = LED(19)

# Global variables for keeping track of the current topic values
LightStatus = ''
rpiA = ''
rpiC = ''

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
	print('Connected with result code ' + str(rc))
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe('LightStatus', 2)         # Set the QOS to 2
	client.subscribe('Status/RaspberryPiA', 2) # Set the QOS to 2
	client.subscribe('Status/RaspberryPiC', 2) # Set the QOS to 2

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    s = 'Topic: ' + msg.topic
    s += '\nMessage: ' + msg.payload.decode()
    print(s)

    # Turn LED's on/off

    # - LED1 -- "LightStatus" topic
    #   o if no value yet -- keep off the light
    #   o "TurnOff" -- turn off the light
    #   o "TurnOn" -- turn on the light
    # - LED2 -- "Status/RaspberryPiA" topic
    #   o "offline" -- turn off the light
    #   o "online" -- turn on the light
    # - LED3 -- "Status/RaspberryPiC" topic
    #   o "offline" -- turn off the light (for LED1 AND LED3)
    #   o "online" -- turn on the light
    if (msg.topic == 'LightStatus'):
        global LightStatus
        LightStatus = msg.payload.decode()

        if (msg.payload.decode() == 'TurnOff'):
            GPIO.output(21, False)
        elif (msg.payload.decode() == 'TurnOn'):
            GPIO.output(21, True)
        else:
            print('Invalid (topic = ' + msg.topic + ', payload = ' + msg.payload.decode() + ')')
    elif (msg.topic == 'Status/RaspberryPiA'):
        global rpiA
        rpiA = msg.payload.decode()

        if (msg.payload.decode() == 'offline'):
            GPIO.output(26, False)
        elif (msg.payload.decode() == 'online'):
            GPIO.output(26, True)
        else:
            print('Invalid (topic = ' + msg.topic + ', payload = ' + msg.payload.decode() + ')')
    elif (msg.topic == 'Status/RaspberryPiC'):
        global rpiC
        rpiC = msg.payload.decode()

        if (msg.payload.decode() == 'offline'):
            GPIO.output(21, False)
            GPIO.output(19, False)
        elif (msg.payload.decode() == 'online'):
            GPIO.output(19, True)
        else:
            print('Invalid (topic = ' + msg.topic + ', payload = ' + msg.payload.decode() + ')')
    else:
        print('Invalid topic: ' + msg.topic)

# Setup the lights
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)

# Initialize all lights to OFF
GPIO.output(21, False)
GPIO.output(26, False)
GPIO.output(19, False)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# TODO: Connect to a remote broker, not localhost
client.connect('192.168.43.112', 1883, 5)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
