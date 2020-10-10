#!/bin/env python

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
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

def send_bars(bars):
    socketio.emit('bars', bars)
    return

import random
import time

@celery.task(bind=True)
def progress_bar(self):

    tasks = [
        {
            'progress': 20,
            'message': "connecting to API"
        },
        {
            'progress': 40,
            'message': "getting records"
        },
        {
            'progress': 60,
            'message': "calculating"
        },
        {
            'progress': 80,
            'message': "changing values"
        },
        {
            'progress': 100,
            'message': "completed!"
        }
    ]
    for task in tasks:
        self.update_state(state = "Progress", meta = task)
        time.sleep(1)    
    return


@socketio.on('socketio_progress_bar')
def socketio_progress_bar():
    task = progress_bar.delay()
    result = progress_bar.AsyncResult(task.id)
    old_result = ""
    for i in range(0,10):

        if result.info == None:
            break
        if result.info == old_result:
            continue
        
        bar = [{
            'id': task.id,
            'progress': result.info['progress'],
            'message': result.info['message']
        }]
        emit('bars', bar)
        old_result = result.info
        socketio.sleep(1)
    return

@app.route('/')
def index():
    # result = add_together.delay(23, 42)
    # print("hello " + str(result.wait()))  # 65
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug = True)