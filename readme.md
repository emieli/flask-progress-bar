https://github.com/jacoborus/nanobar/archive/master.zip
Import nanobar.min.js

apt install python3-pip git curl
pip3 install flask flask-socketio flask-celery eventlet redis

How to start:
./run_redis.sh & celery -A app.celery worker & python3 app.py