#!/bin/env python

from time import sleep

import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit

from rq import Queue
from rq.job import Job
from redis import Redis
from tasks import task_create_host

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'

# SocketIO
socketio = SocketIO(app, message_queue='redis://')

# Redis-queue
redis_conn = Redis()
q = Queue(connection=redis_conn) 

@socketio.on('create_host')
def create_host(data):
    task = q.enqueue(task_create_host, **data)
    socketio.emit('new_task', task.id)
    return

@socketio.on('get_task_updates')
def task_updates(tasks):
    ''' Send current task status to client '''

    # print(q.started_job_registry.get_job_ids())
    results = {}
    for task in tasks.keys():
        task = Job.fetch(task, connection=redis_conn)
        if task.get_status() == "finished":
            results[task.id] = {
                'status': task.get_status(),
                'meta': {'message': task.result}
            }
        else:
            results[task.id] = {
                'status': task.get_status(),
                'meta': task.meta
            }
    socketio.emit('task_updates', results)

@app.route('/')
def index():
    ''' Render webpage '''
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug = True)