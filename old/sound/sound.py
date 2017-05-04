import os
import sys
import paho.mqtt.client as mqtt
from time import sleep
import datetime
from _thread import *

sys.path.append('/home/pi/453Project/utils')
import Constants

SLEEP = 2
CLIENT_ID = 'RaspiC'
PSWD = 'passwordC'


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print('Connected with result code ' + str(rc))


# Handles the publishing
def publisher_thread():
    while True:
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
        print("Sending to broker: " + msg_read)

        client.publish(topic=Constants.PEOPLE_STATUS_TOPIC, payload=msg_read, qos=2, retain=True)

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
