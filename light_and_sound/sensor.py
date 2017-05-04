# Publisher

# ------------------------------------------------------
# ------------------ Description -----------------------
# ------------------------------------------------------

# Publish to (QoS == 2):
# - lightSensor (from the LDR)
#      - kitchen
#      - corner
#      - sunlight
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
import os
import paho.mqtt.client as mqtt
from time import sleep
import datetime
from _thread import *
from gpiozero import MCP3008, MCP3204, LED
import socket

sys.path.append('/home/pi/453Project/utils')

import Constants

# Set the correct channel
CORNER_CHANNEL = 0
KITCHEN_CHANNEL = 1
SUN_CHANNEL = 0
CLIENT_ID = ''
PSWD = ''


def usage():
    print('Usage: python3 sensor.py <topic_name>\n' +
          'where <topic_name> one of the following:\n'
          '  - corner\n' +
          '  - others')
    exit()

# Set the topic
if len(sys.argv) < 2:
    usage()

IP_ADDRESS = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
                           if not ip.startswith("127.")][:1],
                          [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close())
                            for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

if sys.argv[1] == 'others':
    CLIENT_ID = 'RaspiA'
    PSWD = 'passwordA'
    LDR_CHANNEL = 1
    others = True
elif sys.argv[1] == 'corner':
    if IP_ADDRESS != '192.168.1.143':
        print("This is not the Living Room Pi.  SSH to 192.168.1.143 and try again.")
        exit() 
    CLIENT_ID = 'RaspiC'
    PSWD = 'passwordC'
    others = False
else:
    usage()

# Set the amt of time to sleep between publishes
SLEEP = 2

# The number to scale the LDR with
SCALE = 2.1276595744681

if sys.argv[1] == "others":
    kitchenFile = open("/home/pi/453Project/light_and_sound/data/kitchenData.txt", 'a')
    sunFile = open("/home/pi/453Project/light_and_sound/data/sunlightData.txt", 'a')
else:
    file = open("/home/pi/453Project/light_and_sound/data/cornerData.txt", 'a')

# Set constants for various topics
KITCHEN_READING_TOPIC = Constants.LIGHT_READING_TOPIC + "kitchen"
KITCHEN_STATUS_TOPIC = Constants.LIGHT_STATUS_TOPIC + "kitchen"

SUN_READING_TOPIC = Constants.LIGHT_READING_TOPIC + "sunlight"
SUN_STATUS_TOPIC = Constants.LIGHT_STATUS_TOPIC + "sunlight"

CORNER_READING_TOPIC = Constants.LIGHT_READING_TOPIC + "corner"
CORNER_STATUS_TOPIC = Constants.LIGHT_STATUS_TOPIC + "corner"

# Set global variables to store the most-recent LDR value
kitchen_lastLDR = 0
sunlight_lastLDR = 0
corner_lastLDR = 0

# Set global variables to store the most-recent light status
kitchen_lastStatus = "Off"
sunlight_lastStatus = "Off"
corner_lastStatus = "Off"


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print('Connected with result code ' + str(rc))

    if others:
        client.subscribe(KITCHEN_READING_TOPIC, 2)  # Set the QOS to 2
        client.subscribe(SUN_READING_TOPIC, 2)  # Set the QOS to 2

        client.subscribe(KITCHEN_STATUS_TOPIC, 2)  # Set the QOS to 2
        client.subscribe(SUN_STATUS_TOPIC, 2)  # Set the QOS to 2
    else:
        client.subscribe(CORNER_READING_TOPIC, 2)  # Set the QOS to 2
        client.subscribe(CORNER_STATUS_TOPIC, 2)  # Set the QOS to 2


def on_message(client, userdata, msg):
    global kitchen_lastLDR
    global sunlight_lastLDR
    global corner_lastLDR

    global kitchen_lastStatus
    global sunlight_lastStatus
    global corner_lastStatus

    content = msg.payload.decode()
    if msg.topic == KITCHEN_READING_TOPIC:
        l = content.split(',')
        kitchen_lastLDR = float(l[1])
    elif msg.topic == SUN_READING_TOPIC:
        l = content.split(',')
        sunlight_lastLDR = float(l[1])
    elif msg.topic == CORNER_READING_TOPIC:
        l = content.split(',')
        corner_lastLDR = float(l[1])
    elif msg.topic == KITCHEN_STATUS_TOPIC:
        l = content.split(',')
        kitchen_lastStatus = l[1]
    elif msg.topic == SUN_STATUS_TOPIC:
        l = content.split(',')
        sunlight_lastStatus = l[1]
    elif msg.topic == CORNER_STATUS_TOPIC:
        l = content.split(',')
        corner_lastStatus = l[1]
    else:
        print('Invalid topic: ' + msg.topic)


# Handles the publishing thread
def publisher_thread():

    while True:
        if sys.argv[1] == "others":
            # Handle the sound publishing
            os.system("timeout 5 arecord -f dat -D plughw:1 a.wav")
            out = os.popen("sox a.wav -n stat 2> test.txt; grep \"Maximum amplitude\" test.txt | cut -d \":\" -f 2")
            line = out.readline()
            print(line)

            to_send = Constants.PEOPLE_ABSENT
            if float(line) > .002400:
                print("Someone is in the room")
                to_send = Constants.PEOPLE_PRESENT
            else:
                print("No one is in the room")

            currentTime = datetime.datetime.now()
            msg_read = str(currentTime) + ',' + to_send
            print("Sound: " + msg_read)

            client.publish(topic=Constants.PEOPLE_STATUS_TOPIC, payload=msg_read, qos=2, retain=True)

            # Handle the light publishing
            sunLDR = MCP3204(channel=SUN_CHANNEL).value * SCALE
            kitchenLDR = MCP3204(channel=KITCHEN_CHANNEL).value * SCALE

            currentTime = datetime.datetime.now()
            msg1 = str(currentTime) + ',' + str(kitchenLDR)
            msg2 = str(currentTime) + ',' + str(sunLDR)
            print("kitchen value: " + msg1)
            print("sunlight value: " + msg2)

            client.publish(topic=KITCHEN_READING_TOPIC, payload=msg1, qos=2, retain=True)
            client.publish(topic=SUN_READING_TOPIC, payload=msg2, qos=2, retain=True)

            # Write to file
            kData = str(kitchenLDR) + "," + str(currentTime) + "\n"
            kitchenFile.write(kData)
            sData = str(sunLDR) + "," + str(currentTime) + "\n"
            sunFile.write(sData)

            # Classification portion
            global kitchen_lastLDR
            global sunlight_lastLDR

            currentTime = datetime.datetime.now()
            justTime = int(currentTime.strftime('%H'))
            if 8 <= justTime <= 19:
                # Day Time

                # The kitchen status
                if kitchen_lastLDR - kitchenLDR > 0 and abs(kitchen_lastLDR - kitchenLDR) > .06:
                    kitchen_status = Constants.LIGHT_OFF
                elif kitchen_lastLDR - kitchenLDR < 0 and abs(kitchen_lastLDR - kitchenLDR) > .06:
                    kitchen_status = Constants.LIGHT_ON
                else:
                    kitchen_status = kitchen_lastStatus

                # The sunlight status
                if sunlight_lastLDR - sunLDR > 0 and abs(sunlight_lastLDR - sunLDR) > .1:  # subject to change based on more data we get
                    sunlight_status = Constants.LIGHT_OFF
                elif sunlight_lastLDR - sunLDR < 0 and abs(sunlight_lastLDR - sunLDR) > .1:
                    sunlight_status = Constants.LIGHT_ON
                else:
                    sunlight_status = sunlight_lastStatus
            elif 8 > justTime > 19:
                # Night Time

                # The kitchen status
                if kitchen_lastLDR - kitchenLDR > 0 and abs(kitchen_lastLDR - kitchenLDR) > .15:
                    kitchen_status = Constants.LIGHT_OFF
                elif kitchen_lastLDR - kitchenLDR < 0 and abs(kitchen_lastLDR - kitchenLDR) > .15:
                    kitchen_status = Constants.LIGHT_ON
                else:
                    kitchen_status = kitchen_lastStatus

                # The sunlight status
                sunlight_status = Constants.LIGHT_OFF

            # Publish the statuses found by the classification model
            msg1 = str(currentTime) + ',' + kitchen_status
            msg2 = str(currentTime) + ',' + sunlight_status
            print("Kitchen: " + msg1)
            print("Sunlight: " + msg2)

            client.publish(topic=KITCHEN_STATUS_TOPIC, payload=msg1, qos=2, retain=True)
            client.publish(topic=SUN_STATUS_TOPIC, payload=msg2, qos=2, retain=True)
        else:
            cornerLDR = MCP3204(channel=CORNER_CHANNEL).value * SCALE

            currentTime = datetime.datetime.now()
            msg = str(currentTime) + ',' + str(cornerLDR)
            print("corner value: " + msg)

            # Publish Data
            client.publish(topic=CORNER_READING_TOPIC, payload=msg, qos=2, retain=True)

            # Write to file
            data = str(cornerLDR) + "," + str(currentTime) + "\n"
            file.write(data)

            # Classification portion
            global corner_lastLDR

            currentTime = datetime.datetime.now()
            justTime = int(currentTime.strftime('%H'))

            if 8 <= justTime <= 19:
                # Day Time

                if corner_lastLDR - cornerLDR > 0 and abs(corner_lastLDR - cornerLDR) > .07:
                    corner_status = Constants.LIGHT_OFF
                elif corner_lastLDR - cornerLDR < 0 and abs(corner_lastLDR - cornerLDR) > .07:
                    corner_status = Constants.LIGHT_ON
                else:
                    corner_status = corner_lastStatus
            elif 8 > justTime > 19:
                # Night Time

                if corner_lastLDR - cornerLDR > 0 and abs(corner_lastLDR - cornerLDR) > .14:
                    corner_status = Constants.LIGHT_OFF
                elif corner_lastLDR - cornerLDR < 0 and abs(corner_lastLDR - cornerLDR) > .14:
                    corner_status = Constants.LIGHT_ON
                else:
                    corner_status = corner_lastStatus

            # Publish the statuses found by the classification model
            msg = str(currentTime) + ',' + corner_status
            print("Corner: " + msg)

            client.publish(topic=CORNER_STATUS_TOPIC, payload=msg, qos=2, retain=True)

        # Only query every X seconds
        sleep(SLEEP)

# Set up the client mosquitto connection
client = mqtt.Client(client_id=CLIENT_ID, clean_session=False) # retain flag (clean_session) = false
client.username_pw_set(CLIENT_ID, password=PSWD)
client.on_connect = on_connect
client.on_message = on_message

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

kitchenFile.close()
sunFile.close()
file.close()
