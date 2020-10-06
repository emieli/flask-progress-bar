#!/bin/env python

from flask import render_template

from app import create_app, socketio
app = create_app()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug = True)