https://github.com/jacoborus/nanobar/archive/master.zip
Import nanobar.min.js

apt install python3-pip git curl redis
pip3 install flask flask-socketio flask-celery eventlet

How to start:
# ./run_redis.sh &
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