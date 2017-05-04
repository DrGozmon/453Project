from flask import Flask, json
from flask import render_template
import os
import paho.mqtt.client as mqtt
import sys

sys.path.append('/home/pi/453Project/utils')
import Constants as Constants
from gpiozero import LED
from time import sleep

led2 = LED(2)
led3 = LED(3)

app = Flask(__name__)
port = os.getenv('VCAP_APP_PORT', '5000')

# The light statuses
DEFAULT = "On"
status_kitchen = "On"
status_corner = "On"
status_sunlight = "On"

# The door status
status_door = "Closed"

# The people status
status_people = "No"

''' --------------------------------------
------------- Status Getters -------------
---------------------------------------'''


# Check the status of the light
def get_light_status(location):
    global status_kitchen
    global status_corner
    global status_sunlight

    if location == "kitchen":
        return status_kitchen
    if location == "corner":
        return status_corner
    if location == "sunlight":
        return status_sunlight
    else:
        return "Invalid location"


# Toggle the light to on/off
def toggle_light(location, status):
    global status_kitchen
    global status_corner
    global status_sunlight

    if location != "kitchen" and location != "corner" and location != "sunlight":
        return "Invalid location"
    if status != Constants.LIGHT_ON and status != Constants.LIGHT_OFF:
        return "Invalid status"

    # Don't toggle if it's already at that state
    if location == "kitchen" and status == status_kitchen:
        return
    if location == "corner" and status == status_corner:
        return
    if location == "sunlight" and status == status_sunlight:
        return

    TOPIC = Constants.LIGHT_STATUS_TOPIC + location
    client.publish(topic=TOPIC, payload=status, qos=2, retain=True)


# Get the current status of the door
def get_door_status():
    global status_door
    return status_door


# Get the status of people in the room
def get_people_status():
    global status_people
    return status_people


''' --------------------------------------
-------------- Web App Code --------------
---------------------------------------'''


def get_info():
    data = {"kitchen_status": get_light_status('kitchen'),
            "corner_status": get_light_status('corner'),
            "sunlight_status": get_light_status('sunlight'),
            "door_status": get_door_status(),
            "people_status": get_people_status()}
    html_item = json.dumps(data, indent=2, separators=(', ', ': '))

    return html_item


@app.route('/')
def index():
    return render_template('index.html', info=get_info())


# @app.route('/light/<command>/', methods=['GET', 'POST'])
# def light_route(command):
    # return command
    
@app.route('/kitchen/<command>/', methods=['GET', 'POST'])
def kitchen_route(command):
    global status_kitchen
    if command == "on":
        led3.on()
        status_kitchen = "On"
    elif command == "off":
        led3.off()
        status_kitchen = "Off"
    return render_template('index.html', info=get_info())


@app.route('/corner/<command>/', methods=['GET', 'POST'])
def corner_route(command):
    global status_corner
    if command == "on":
        status_corner = "On"
        led2.on()
    elif command == "off":
        led2.off()
        status_corner = "Off"
    return render_template('index.html', info=get_info())


''' --------------------------------------
------------- Paho Callbacks -------------
---------------------------------------'''


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print('Connected with result code ' + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(Constants.LIGHT_STATUS_TOPIC + '+', 2)         # Set the QOS to 2
    client.subscribe(Constants.DOOR_STATUS_TOPIC, 2)                # Set the QOS to 2
    client.subscribe(Constants.PEOPLE_STATUS_TOPIC, 2)              # Set the QOS to 2


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    s = 'Topic: ' + msg.topic
    s += '\nMessage: ' + msg.payload.decode()
#    file = open('/home/pi/453Project/output.txt', 'a')
#    file.write(s)

    global status_kitchen
    global status_sunlight
    global status_corner
    global status_door
    global status_people

    content = msg.payload.decode()
    if msg.topic == Constants.LIGHT_STATUS_TOPIC + 'kitchen':
        l = content.split(',')
#        file.write("Kitchen status: " + l[1])
#        print("Kitchen status: " + l[1])
        status_kitchen = l[1]
    elif msg.topic == Constants.LIGHT_STATUS_TOPIC + 'sunlight':
        l = content.split(',')
#        file.write("Sunlight status: " + l[1])
#        print("Sunlight status: " + l[1])
        status_sunlight = l[1]
    elif msg.topic == Constants.LIGHT_STATUS_TOPIC + 'corner':
        l = content.split(',')
#        file.write("Corner status: " + l[1])
#        print("Corner status: " + l[1])
        status_corner = l[1]
    elif msg.topic == Constants.DOOR_STATUS_TOPIC:
        l = content.split(',')
#        file.write("Door status: " + l[1])
#        print("Door status: " + l[1])
        status_door = l[1]
    elif msg.topic == Constants.PEOPLE_STATUS_TOPIC:
        l = content.split(',')
#        file.write("People status: " + l[1])
#        print("People status: " + l[1])
        status_people = l[1]
    else:
#        file.write('Invalid topic: ' + msg.topic)
        print('Invalid topic: ' + msg.topic)

#    file.close()


''' --------------------------------------
------------ Startup the app -------------
---------------------------------------'''


if __name__ == '__main__':

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(Constants.BROKER_IP, 1883, 60)
    client.loop_start()

    app.run(host='0.0.0.0', debug=True, port=int(port))

