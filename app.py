#!/bin/env python

import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from celery import Celery

import random
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'

# SocketIO
socketio = SocketIO(app, message_queue='redis://')

# Initialize Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['result_backend'] = 'redis://localhost:6379/0'
app.config['result_expires'] = 30
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task(bind=True)
def progress_bar(self):
    ''' This is an example of a task. A real world example performs actual API calls. '''
    tasks = [
        {'progress': 5,  'message': "connecting to API"},
        {'progress': 20, 'message': "authenticating"},
        {'progress': 40, 'message': "getting records"},
        {'progress': 60, 'message': "calculating"},
        {'progress': 80, 'message': "changing values"},
        {'progress': 99, 'message': "completed!"}
    ]
    for task in tasks:
        self.update_state(state = "Progress", meta = task)
        time.sleep(random.randint(1,3)) # we need a final timeout so that the browser can fetch the task completion before it is removed
    return

tasks = {}

@socketio.on('create_bar')
def create_bar():
    ''' Create a new task '''
    task = progress_bar.delay()
    tasks[task.id] = ""
    return

@socketio.on('request_bar_updates')
def bar_updates():
    ''' Send bar updates to client '''
    results = {}
    for task_id in tasks.keys():
        result = progress_bar.AsyncResult(task_id)
        if result.info == None: # bar expired, don't show it
            continue
        results[task_id] = result.info
    socketio.emit('bar_updates', results)

@app.route('/')
def index():
    ''' Render webpage '''
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug = True)