https://github.com/jacoborus/nanobar/archive/master.zip
Import nanobar.min.js

apt install python3-pip git curl redis python3-venv
pip3 install flask flask-socketio flask-celery eventlet redis
cd /opt/flask-progress-bar
python3 -m venv venv

How to start:
source venv/bin/activate
celery -A app.celery worker --loglevel=INFO &
python3 app.py

How to stop:
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
- Redis is used by Celery to have a central location for all data stored. Whenever "self.update_state" is called, the data is saved in redis.
- Whenever the url 'get_tasks' is fetched by a client browser, Flask checks the "Asyncresult" of each task, which basically returns the current "self.update_state" according to redis. This data is then returned to the client.
- The client is running an ajax script every second that, once the page is loaded, fetches the 'get_tasks' URL every second, and so can retrieve the progress at regular intervals and display the progress with the progress bars it renders on screen.

I would prefer a way where the server updates the client, but I have not found a good way of doing so. 