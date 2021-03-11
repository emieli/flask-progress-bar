#!/bin/env python

import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from celery import Celery, states
from celery.exceptions import Ignore

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

from api_phpipam import phpipam
@celery.task(bind=True)
def task_create_host(self, **kwargs):

    meta = {'progress': 10, 'message': 'Task started'}
    self.update_state(state = "PROGRESS", meta = meta)

    meta = {'progress': 30, 'message': 'Connecting to API...'}
    self.update_state(state = "PROGRESS", meta = meta)
    ipam = phpipam()
    if not ipam.token:
        self.update_state(state = states.FAILURE, meta = 'Unable to connect to API')
        raise Ignore()
    
    time.sleep(2)

    meta = {'progress': 50, 'message': 'Checking if host already exists'}
    self.update_state(state = "PROGRESS", meta = meta)
    host = ipam.get_address(**kwargs)
    
    time.sleep(2)
    if host:
        return { 'message': f"{host[0]['hostname']} already exists, no action."}

    meta = {'progress': 75, 'message': 'Host does not exist, creating...'}
    self.update_state(state = "PROGRESS", meta = meta)
    host = ipam.create_address(subnet_id = 265, payload = {'hostname': kwargs['hostname']})
    
    time.sleep(2)
    if host:
        return { 'message': f"{kwargs['hostname']} created, id: {host['id']}"}

    return

@socketio.on('create_host')
def create_host(data):
    task = task_create_host.delay(**data)
    socketio.emit('new_task', task.id)
    return

@socketio.on('get_task_updates')
def task_updates(tasks):
    ''' Send current task status to client '''
    results = {}
    for task_id in tasks.keys():
        task = task_create_host.AsyncResult(task_id)
        results[task_id] = {
            'status': task.status,
            'info': task.info
        }
    socketio.emit('task_updates', results)

@app.route('/')
def index():
    ''' Render webpage '''
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug = True)