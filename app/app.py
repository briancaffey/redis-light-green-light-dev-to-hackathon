import os
import time
import uuid

from celery import Celery
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room, send


REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PROTOCOL = os.environ.get("REDIS_PROTOCOL", "redis")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
BROKEN_URL_DB_INDEX = "2"
RESULT_BACKEND_DB_INDEX = "3"

celery = Celery(__name__)
celery.conf.broker_url = f"{REDIS_PROTOCOL}://{REDIS_HOST}:{REDIS_PORT}/{BROKEN_URL_DB_INDEX}"
celery.conf.result_backend = f"{REDIS_PROTOCOL}://{REDIS_HOST}:{REDIS_PORT}/{RESULT_BACKEND_DB_INDEX}"

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

###############################################################################
# Celery
###############################################################################

@celery.task(name="create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 2)
    return True

# scheduled tasks using celery beat
celery.conf.beat_schedule = {
    'test-period-task': {
        'task': 'create_task',
        'schedule': 10.0,
        'kwargs': {'task_type': '1'}
    }
}

###############################################################################
# API Routes
###############################################################################

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

###############################################################################
# SocketIO handlers
###############################################################################

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
