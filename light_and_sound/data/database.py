# Subscriber (Mike's RPi)

# ------------------------------------------------------
# ------------------ Description -----------------------
# ------------------------------------------------------

# Subscribe to (QoS == 2):
# - LightStatus/kitchen
# - lightStatus/sunlight
# - lightStatus/corner

# ------------------------------------------------------
# ---------------------- Code --------------------------
# ------------------------------------------------------

import paho.mqtt.client as mqtt
import utils.Constants as Constants


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print('Connected with result code ' + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(Constants.LIGHT_STATUS_TOPIC + '+', 2)         # Set the QOS to 2


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    s = 'Topic: ' + msg.topic
    s += '\nMessage: ' + msg.payload.decode()
    print(s)

    toWrite = msg.payload.decode() + '\n'
    if msg.topic == Constants.LIGHT_STATUS_TOPIC + 'kitchen':
        with open("kitchen.csv", "a") as f:
            f.write(toWrite)
        with open("all_lights.csv", "a") as f:
            f.write(toWrite)
    elif msg.topic == Constants.LIGHT_STATUS_TOPIC + 'sunlight':
        with open("sunlight.csv", "a") as f:
            f.write(toWrite)
        with open("all_lights.csv", "a") as f:
            f.write(toWrite)
    elif msg.topic == Constants.LIGHT_STATUS_TOPIC + 'corner':
        with open("sunlight.csv", "a") as f:
            f.write(toWrite)
        with open("all_lights.csv", "a") as f:
            f.write(toWrite)
    else:
        print('Invalid topic: ' + msg.topic)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# TODO: Connect to a remote broker, not localhost
client.connect(Constants.BROKER_IP, 1883, 5)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
