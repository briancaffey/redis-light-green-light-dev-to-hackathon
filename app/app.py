import os
import random
import time
import uuid

from celery import Celery
from flask import Flask, jsonify, render_template, request, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from flask_session import Session

import redis

# SESSION_TYPE = 'redis'

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PROTOCOL = os.environ.get("REDIS_PROTOCOL", "redis")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
BROKEN_URL_DB_INDEX = "2"
RESULT_BACKEND_DB_INDEX = "3"

celery = Celery(__name__)
celery.conf.broker_url = f"{REDIS_PROTOCOL}://{REDIS_HOST}:{REDIS_PORT}/{BROKEN_URL_DB_INDEX}"
celery.conf.result_backend = f"{REDIS_PROTOCOL}://{REDIS_HOST}:{REDIS_PORT}/{RESULT_BACKEND_DB_INDEX}"

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url(f'redis://{os.environ.get("REDIS_HOST", "redis")}:6379/3')
# app.config['SESSION_COOKIE_DOMAIN'] = os.environ.get("SESSION_COOKIE_DOMAIN", "localhost:3000")
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "secret")
CORS(app)
Session(app)

try:
    r = redis.Redis(
        host=os.environ.get("REDIS_HOST", "redis"),
        port=6379,
        charset="utf-8",
        decode_responses=True
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

@celery.task(name="update_light", ignore_result=True)
def update_light(room, state):
    # update the light of a room
    print(f"update_light: {room} {state}")
    timestamp = round(time.time())
    p = r.pipeline()
    p.hset(room, "light", state)
    p.hset(room, "updated", timestamp)
    p.execute()
    socketio.emit('update_light', {'room': room, 'state': state}, room=room, namespace="/game")

@celery.task(name="update_lights", ignore_result=True)
def update_lights():
    rooms = r.keys("room:*")
    for room in rooms:
        print(room)
        states = ["red", "green"]
        random.shuffle(states)
        state = states[0]
        update_light.delay(room, state)
    return True

# scheduled tasks using celery beat
celery.conf.beat_schedule = {
    'update_lights': {
        'task': 'update_lights',
        'schedule': 2.0,
    }
}

###############################################################################
# API Routes
###############################################################################

@app.route("/api/status/")
def check():
    return "OK"

@app.route("/api/session/set")
def set_session():
    session["id"] = str(uuid.uuid4())
    return jsonify({"id": session["id"]})

@app.route("/api/session/get")
def get_session():
    return session["id"]


@app.route("/api/session", methods=["POST"])
def player_number():
    if session.get("session") is None:
        playerNumber = session.sid # uuid.uuid4()
        session['playerNumber'] = playerNumber
        return jsonify({"playerNumber": playerNumber}), 202
    return jsonify({"playerNumber": session.sid}), 200

@app.route("/api/new", methods=["POST"])
def new_room():
    new_room_id = uuid.uuid4()
    new_room_key = f'room:{new_room_id}'
    timestamp = round(time.time())
    p = r.pipeline()
    p.hset(new_room_key, "light", "red")
    p.hset(new_room_key, "changed", f'{timestamp}')
    p.hset(new_room_key, "created", f'{timestamp}')
    p.execute()

    return jsonify({ "id": new_room_id}), 202

###############################################################################
# Utility Functions
###############################################################################

def get_room_positions(room):
    position_keys = r.keys(f'pos:{room}_*')
    print(position_keys)

    # use a pipeline to get all of the player positions for a room
    p = r.pipeline()

    for k in position_keys:
        p.hgetall(k)

    # execute the pipeline and get the results
    positions = p.execute()

    return positions

###############################################################################
# SocketIO handlers
###############################################################################

@socketio.on('move', namespace='/game')
def handle_move(message):
    """Attempt to move a player forward by one step"""
    print(message)
    room = message['room']
    player = message['player']
    r.hincrby(f'pos:{room}_{player}', 'pos', 1)

    positions = get_room_positions(room)

    emit('update', {"positions": list(positions)}, room=f'room:{room}')


@socketio.on('join', namespace="/game")
def connect_to_game(message):
    # print(session.sid)
    print(message)
    room = message['room']
    player = message['player']

    join_room(f'room:{room}')

    if not r.exists(f'pos:{room}_{player}'):
        p = r.pipeline()
        p.hset(f'pos:{room}_{player}', 'pos', 0)
        p.hset(f'pos:{room}_{player}', 'state', 'alive')
        p.hset(f'pos:{room}_{player}', 'player', player)
        p.execute()

    # update the room with positions for all players
    positions = get_room_positions(room)
    emit('update', {"positions": list(positions)}, room=f'room:{room}')

    send(f'User {player} has joined room room:{room} at position 0', room=f'room:{room}')
