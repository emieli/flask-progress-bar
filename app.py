#!/bin/env python

from flask import Flask, render_template
from flask_socketio import SocketIO
from celery import Celery

app = Flask(__name__)
app.debug = True
app.clients = {}

app.config['SECRET_KEY'] = 'top-secret!'
# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['result_backend'] = 'redis://localhost:6379/0'

# SocketIO
socketio = SocketIO(app)

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task()
def add_together(a, b):
    return a + b

@app.route('/')
def index():
    result = add_together.delay(23, 42)
    print("hello " + str(result.wait()))  # 65
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug = True)