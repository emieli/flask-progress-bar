https://github.com/jacoborus/nanobar/archive/master.zip
Import nanobar.min.js

# Installation:
apt install python3-pip git curl redis python3-venv
pip3 install flask flask-socketio flask-celery eventlet redis
cd /opt/flask-progress-bar
python3 -m venv venv

# How to start:
source venv/bin/activate
celery -A app.celery worker --loglevel=INFO &
python3 app.py

How to stop Celery:
Run command "fg" and then do Ctrl+C

# show redis data:
emil@flask-progress-1:/opt/flask-progress-bar$ redis-cli

127.0.0.1:6379> KEYS *
2) "celery-task-meta-5ee49902-bfaa-49fe-8eb8-59a0608d6b85"

127.0.0.1:6379> GET celery-task-meta-5ee49902-bfaa-49fe-8eb8-59a0608d6b85
"{\"status\": \"SUCCESS\", \"result\": [{\"progress\": 37}, {\"progress\": 25}, {\"progress\": 82}], \"traceback\": null, \"children\": [], \"date_done\": \"2020-10-10T08:40:06.032136\", \"task_id\": \"5ee49902-bfaa-49fe-8eb8-59a0608d6b85\"}"

# Celery notes
When you changes the code in a Celery task, reload the Celery worker process.

# How does this all work?
The goal of this webpage was setting up background workers that could perform API tasks in the background, while still allowing the frontend webpage to display up-to-date information on the progress of these tasks.

- Flask hosts the webpage that the user connects to.
- Celery hosts the background tasks that are simulating API actions.
- Redis is used by Celery tasks to store task progress data. Whenever "self.update_state" is called in a celery task, that data is saved in redis.

So a user connects to connects to the flask which renders and returns index.html. The html file contains javascript that setups up a websocket connection and triggers the "request_bar_updates" function every second. This allows the webpage to continuously retrieve bar updates for existing bars.

Additionally, the webpage has a button to create new bars. Once pressed, a request is sent to Flask via websocket, creating a new celery task via the "progress_bar.delay()" function. This task does some things and sends updates on its progress along the way.

Every second the user browser requests bar updates from Flask. Flask asks for updates via the "progress_bar.AsyncResult()" function, which either talks to redis or celery directly, am unsure. Once the relevant bar updates have been retrieved from celery/redis, flask sends them to the client via websocket using the "bar_updates" function. The bars, if not exists, are created by the browser. Existing bars are updated with the latest data.