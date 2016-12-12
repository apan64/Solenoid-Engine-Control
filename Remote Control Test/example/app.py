#!/usr/bin/env python

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on available packages.
async_mode = None

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print('async_mode is ' + async_mode)

# monkey patching is necessary because this application uses a background
# thread
if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()

import time
from threading import Thread
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fookin \'ell, m8, i\'ll correspondence yer \'ead in, swear on me mum'
socketio = SocketIO(app, async_mode=async_mode)
thread = None


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while 1==2:
        time.sleep(10)
        count += 1
        print count
        socketio.emit('my response',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/test')

@app.route('/')
def index():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()
    return render_template('index.html')

@app.route('/test.html')
def test():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()
    return render_template('test.html')



arduino = None

@socketio.on('arduino_control',namespace='/test')
def serial_start(message):
    import serial
    global arduino 
    arduino = serial.Serial('COM7', 9600, timeout=0.5, dsrdtr = True)

@socketio.on('send_to_arduino',namespace='/test')
def serial_control(message):
    print 'sending %s to arduino!' %(message['data'])
    global arduino
    arduino.write(message['data'].encode('UTF-8'))






### Previous Code ###


@socketio.on('movementMessage', namespace='/test')
def hold_down(message): #message is one the built-in events that flask-socketIO has. A named custom event might work better - we want to control and log. 
    session['receive_count'] = session.get('receive_count', 0) + 1
    writeToFile(message['data'],'test.txt')
    print message['data']
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']})

@socketio.on('testButtonClicked', namespace='/test')
def test(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    writeToFile(message['data'],'test.txt')
    print 'test button clicked'
    emit('my response',
         {'data': 'test button clicked', 'count': session['receive_count']})


def writeToFile(message, path):
    with open(path,'w') as f:
        f.write(message)



@socketio.on('close room', namespace='/test')
def close(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         room=message['room'])
    close_room(message['room'])


@socketio.on('my room event', namespace='/test')
def send_room_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']},
         room=message['room'])


@socketio.on('disconnect request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)
