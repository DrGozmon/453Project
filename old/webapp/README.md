This folder contains the web app code. See below for a
description of the files and what they do.

server.py
- This will be actually used for the deployed server.
- Uses MQTT to get various messages pertaining to light /
door statuses.
- Renders `index.html` when user goes to page.
- Contains various methods to call from HTML when turning
on / off the lights.

temp_server.py
- This is the testing version of the server
- Sends dummy JSON object to HTML page to demonstrate
use

templates/index.html
- This contains the html for the only page of the
web app
- Uses passed JSON object to determine statuses of items
- Refreshes itself every 60 seconds (in script at top)