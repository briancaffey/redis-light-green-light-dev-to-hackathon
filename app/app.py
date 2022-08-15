import os
import time
import uuid


from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room, send

from tasks import create_task

import redis

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'secret!'

try:
    r = redis.Redis(
        host=os.environ.get("REDIS_HOST", "redis"),
        port=6379,
    )
except:
    pass

MESSAGE_QUEUE = f'redis://{os.environ.get("REDIS_HOST", "redis")}:6379/1'
# socketio = SocketIO(app, message_queue=MESSAGE_QUEUE, cors_allowed_origins='*')
print(MESSAGE_QUEUE)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='gevent',
    logger=True,
    message_queue=MESSAGE_QUEUE,
)

@socketio.on('connect')
def connect():
    print('Client is connected')

@socketio.on('message')
def handle_message(message):
    print('got a new message!!!!!!!')
    print(message)

@socketio.on('message', namespace='/test')
def handle_message_test_namespace(message):
    print('got a new message from the test namespace!!')
    print(message)


@app.route("/api/status/")
def check():
    return "OK"

@app.route("/task", methods=["POST"])
def run_task():
    content = request.json
    task_type = content["type"]
    task = create_task.delay(int(task_type))
    return jsonify({"task_id": task.id}), 202

@app.route("/new", methods=["POST"])
def new_room():
    new_room_id = uuid.uuid4()
    new_room_key = f'room_{new_room_id}'
    timestamp = round(time.time())
    p = r.pipeline()
    p.hset(new_room_key, "light", "red")
    p.hset(new_room_key, "changed", f'{timestamp}')
    p.execute()

    return jsonify({ "id": new_room_id}), 202


@socketio.on('move', namespace='/game')
def handle_move(message):
    """Attempt to move a player forward by one step"""
    print(message)
    room = message['room']
    player = message['player']
    r.hincrby(f'{room}_{player}', 'pos', 1)


@socketio.on('join', namespace="/game")
def connect_to_game(message):
    print('Client is connected to game')
    print(message)
    room = message['room']
    player = message['player']

    join_room(room)

    p = r.pipeline()
    p.hset(f'{room}_{player}', 'pos', 0)
    p.hset(f'{room}_{player}', 'state', 'alive')
    p.execute()

    send(f'User {player} has joined room {room} at position 0', room=room)
