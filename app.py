#!/bin/env python

import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from celery import Celery

app = Flask(__name__)
app.debug = True
app.clients = {}

app.config['SECRET_KEY'] = 'top-secret!'
# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['result_backend'] = 'redis://localhost:6379/0'
app.config['result_expires'] = 10

# SocketIO
socketio = SocketIO(app, message_queue='redis://')

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

def send_bars(bars):
    socketio.emit('bars', bars)
    return

import random
import time

@celery.task(bind=True)
def progress_bar(self):

    tasks = [
        {'progress': 20, 'message': "connecting to API"},
        {'progress': 40, 'message': "getting records"},
        {'progress': 60, 'message': "calculating"},
        {'progress': 80, 'message': "changing values"},
        {'progress': 99, 'message': "completed!"}
    ]
    for task in tasks:
        self.update_state(state = "Progress", meta = task)
        time.sleep(random.randint(1,3))    
    return

tasks = {}

@socketio.on('create_bar')
def create_bar():

    ''' Create a new task '''
    task = progress_bar.delay()
    tasks[task.id] = ""
    return

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_tasks')
def get_tasks():
    results = {}
    for task_id in tasks.keys():
        result = progress_bar.AsyncResult(task_id)
        if result.info == None: continue
        results[task_id] = result.info
    return jsonify(results)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug = True)