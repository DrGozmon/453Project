from flask import Flask, json
from flask import render_template
import os

app = Flask(__name__)
port = os.getenv('VCAP_APP_PORT', '5000')

# The light statuses
status_kitchen = "On"
status_corner = "On"
status_sunlight = "On"

# The door status
status_door = "Closed"

''' --------------------------------------
------------- Status Getters -------------
---------------------------------------'''


# Check the status of the light
def get_light_status(location):
    if location == "kitchen":
        return status_kitchen
    if location == "corner":
        return status_corner
    if location == "sunlight":
        return status_sunlight
    else:
        return "Invalid location"


# Get the current status of the door
def get_door_status():
    return status_door


''' --------------------------------------
-------------- Web App Code ---------------
---------------------------------------'''


def get_info():
    data = {"kitchen_status": get_light_status('kitchen'),
            "corner_status": get_light_status('corner'),
            "sunlight_status": get_light_status('sunlight'),
            "door_status": get_door_status()}

    return json.dumps(data)


@app.route('/')
def index():
    return render_template('index.html', info=get_info())


@app.route('/light/<command>/', methods=['GET', 'POST'])
def light_route(command):
    return command


''' --------------------------------------
------------ Startup the app -------------
---------------------------------------'''


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
