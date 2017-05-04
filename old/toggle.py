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
import RPi.GPIO as GPIO

sys.path.append('/home/pi/453Project/utils')

import Constants

LED_GPIO = 0

if len(sys.argv) != 2:
    print('Usage: python3 toggle.py <lightName>' +
          'where <lightName> one of the following:\n'
          '  - corner' +
          '  - kitchen')
    exit()

lightName = sys.argv[1]

TOPIC = Constants.LIGHT_STATUS_TOPIC + sys.argv[1]


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    output = 'Connected with result code ' + str(rc) + '\n'
    print(output)

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(TOPIC, qos=2)  # Set the QOS to 2


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    s = 'Topic: ' + msg.topic
    s += '\n   Message: ' + msg.payload.decode()
    s += '\n   TimeStamp: ' + str(datetime.datetime.now().time())

    print(s + '\n')

    if msg.topic == TOPIC:
        if msg.payload.decode() == Constants.LIGHT_OFF:
            GPIO.output(LED_GPIO, False)
        elif msg.payload.decode() == Constants.LIGHT_ON:
            GPIO.output(LED_GPIO, True)
        else:
            print('Invalid (topic = ' + msg.topic + ', payload = ' + msg.payload.decode() + ')')
    else:
        output = 'Invalid topic: ' + msg.topic
        print(output + '\n')

client = mqtt.Client()

client.username_pw_set("Laptop", password="passwordD")
client.on_connect = on_connect
client.on_message = on_message

client.connect(Constants.BROKER_IP, 1883, 5)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
