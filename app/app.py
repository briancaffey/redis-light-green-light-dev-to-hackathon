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

@app.route("/api/rooms", methods=["GET"])
def get_rooms():
    rooms = r.keys("room:*")
    return jsonify(rooms)

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

    # check to see if the player is dead
    # the client should prevent this from happening
    if r.hget(f'pos:{room}_{player}', 'state') == 'dead':
        print("player is dead, do nothing")
        return

    # if the light is green, move the player forward
    light = r.hget(f'room:{room}', "light")
    print(f"light: {light}")

    if light == "green":
        value = r.hincrby(f'pos:{room}_{player}', 'pos', 1)
        if value == 100:
            pass

    # if the light is red, do not move the player forward and set the player state to "dead"
    if light == "red":
        r.hset(f'pos:{room}_{player}', 'state', 'dead')

    positions = get_room_positions(room)

    emit('update', {"positions": list(positions)}, room=f'room:{room}')


@socketio.on('join', namespace="/game")
def connect_to_game(message):
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

@socketio.on('disconnect', namespace="/game")
def disconnect(message):
    print('disconnected')
    room, player = message['room'], message['player']
    print(room, player)
    # remove the pos key for the room/player
    print("deleting pos key")
    r.delete(f'pos:{room}_{player}')
    # delete the room if there are no players left in the room
    if not r.keys(f'pos:{room}_*'):
        print("closing room...")
        # close the room
        close_room(f'room:{room}')
