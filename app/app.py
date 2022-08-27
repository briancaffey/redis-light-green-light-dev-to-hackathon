import os
import random
import time
import uuid

from celery import Celery
from flask import Flask, jsonify, session, request
from flask_cors import CORS
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room, close_room, send, disconnect
import redis

from redis_om import Field, get_redis_connection, HashModel, Migrator

###############################################################################
# Redis OM Models
###############################################################################


class Room(HashModel):
    room: uuid.UUID = Field(index=True)
    light: str
    changed: int
    created: int


class Position(HashModel):
    pos: int
    state: str
    player: uuid.UUID = Field(index=True)
    room: uuid.UUID = Field(index=True)


Migrator().run()

###############################################################################
# Constants
###############################################################################


class PlayerState:
    ALIVE = "alive"
    DEAD = "dead"


class LightState:
    RED = "red"
    GREEN = "green"


class EventType:
    CREATED = "created"
    LIGHT = "light"
    JOIN = "join"
    MOVE = "move"
    WIN = "win"
    DIE = "die"
    LEAVE = "leave"
    END = "end"


FINISH_LINE = 5

###############################################################################
# Configure Celery
###############################################################################

REDIS_PROTOCOL = os.environ.get("REDIS_PROTOCOL", "redis")
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
BROKEN_URL_DB_INDEX = "2"
RESULT_BACKEND_DB_INDEX = "3"

celery = Celery(__name__)
celery.conf.broker_url = (
    f"{REDIS_PROTOCOL}://{REDIS_HOST}:{REDIS_PORT}/{BROKEN_URL_DB_INDEX}"
)
celery.conf.result_backend = (
    f"{REDIS_PROTOCOL}://{REDIS_HOST}:{REDIS_PORT}/{RESULT_BACKEND_DB_INDEX}"
)

###############################################################################
# Configure Flask
###############################################################################


app = Flask(__name__)
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = redis.from_url(
    f'redis://{os.environ.get("REDIS_HOST", "redis")}:6379/3'
)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "secret")

CORS(app)
Session(app)

try:
    # without passing decode_responses=True it was not decoding responses
    om_redis_conn = get_redis_connection(decode_responses=True)
except:
    raise Exception("Could not get redis connection. Make sure REDIS_OM_URL is set.")

###############################################################################
# Configure Flask-SocketIO
###############################################################################

MESSAGE_QUEUE = f'redis://{os.environ.get("REDIS_HOST", "redis")}:6379/1'

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="gevent",
    logger=True,
    message_queue=MESSAGE_QUEUE,
)

###############################################################################
# Celery
###############################################################################


@celery.task(name="update_light", ignore_result=True)
def update_light(room, state):
    """Update the light of a room"""
    timestamp = round(time.time())

    # get the room and update the light state
    om_room = Room.find(Room.room == room).first()
    om_room.update(light=state, changed=timestamp)
    om_room.save()

    # record light update in the redis stream
    om_redis_conn.xadd(
        f"stream:{room}", {"event": EventType.LIGHT, "light": state, "room": room}
    )

    # broadcast the new light state to all connected clients
    socketio.emit(
        "update_light",
        {"room": room, "state": state},
        room=f"room:{room}",
        namespace="/game",
    )


@celery.task(name="update_lights", ignore_result=True)
def update_lights():
    """Get all active game rooms and update submit new task to update light state"""

    # get all rooms
    rooms = Room.find().all()

    # loop over rooms and add a celery task to update the light for each room
    for room in rooms:
        states = [LightState.RED, LightState.GREEN]
        random.shuffle(states)
        state = states[0]

        update_light.delay(room.room, state)

    return True


# scheduled tasks using celery beat
celery.conf.beat_schedule = {
    "update_lights": {
        "task": "update_lights",
        "schedule": 2.0,
    }
}

###############################################################################
# API Routes
###############################################################################


@app.route("/api/status/")
def check():
    return "OK"


@app.route("/api/new", methods=["POST"])
def new_room():
    new_room_id = uuid.uuid4()
    timestamp = round(time.time())

    room = Room(
        room=new_room_id, light=LightState.RED, changed=timestamp, created=timestamp
    )

    room.save()

    om_redis_conn.xadd(f"stream:{new_room_id}", {"event": EventType.CREATED})

    return jsonify({"id": room.room}), 202


@app.route("/api/rooms", methods=["GET"])
def get_rooms():
    """Get all rooms. Note: this does not support pagination"""
    om_rooms = Room.find().all()

    rooms = [{"room": str(room.room)} for room in om_rooms]

    return jsonify({"rooms": rooms}), 200


@app.route("/api/rooms/<room>/events")
def get_events(room):
    events = om_redis_conn.xrange(f"stream:{room}", min="-", max="+")
    return jsonify({"events": events})


###############################################################################
# Utility Functions
###############################################################################


def get_room_positions_om(room):
    """Get all positions for `room`"""

    positions = Position.find(Position.room == room).all()

    # serialize to json
    # player has type of UUID which needs to be converted to a string
    positions = [
        {"player": str(p.player), "pos": p.pos, "state": p.state} for p in positions
    ]

    return positions


###############################################################################
# SocketIO handlers
###############################################################################


@socketio.on("move", namespace="/game")
def handle_move(message):
    """Attempt to move a player forward by one step"""
    room = message["room"]
    player = message["player"]

    # check to see if the player is dead
    # the client should prevent this from happening

    position = Position.find(
        (Position.player == player) & (Position.room == room)
    ).first()

    if position.state == PlayerState.DEAD:
        app.logger.info("Player is dead, do nothing.")
        return

    # if the light is green, move the player forward
    om_room = Room.find(Room.room == room).first()

    if om_room.light == LightState.GREEN:
        value = position.pos
        if value == FINISH_LINE:
            om_redis_conn.xadd(
                f"stream:{room}", {"event": EventType.WIN, "player": player}
            )
            # player wins
            pass
        if value < FINISH_LINE:
            key = position.key()
            new_pos = om_redis_conn.hincrby(key, "pos", 1)
            om_redis_conn.xadd(
                f"stream:{room}",
                {
                    "event": EventType.MOVE,
                    "player": player,
                    "room": room,
                    "pos": new_pos,
                },
            )

    if om_room.light == LightState.RED:
        key = position.key()
        om_redis_conn.hset(key, "state", PlayerState.DEAD)
        om_redis_conn.xadd(
            f"stream:{room}",
            {
                "event": EventType.DIE,
                "player": player,
                "room": room,
                "pos": position.pos,
            },
        )

    positions = get_room_positions_om(room)

    emit("update", {"positions": list(positions)}, room=f"room:{room}")


@socketio.on("join", namespace="/game")
def connect_to_game(message):
    """Handler for when a player joins a room"""
    room = message["room"]
    player = message["player"]

    app.logger.info(f"Player {player} is joining room {room}")

    join_room(f"room:{room}")

    om_player_position = Position.find(
        (Position.room == room) & (Position.player == player)
    ).all()

    if not om_player_position:
        position = Position(room=room, player=player, pos=0, state=PlayerState.ALIVE)

        position.save()

    # update the room with positions for all players
    positions = get_room_positions_om(room)
    emit("update", {"positions": list(positions)}, room=f"room:{room}")

    om_redis_conn.xadd(
        f"stream:{room}",
        {"event": EventType.JOIN, "player": player, "room": room, "pos": 0},
    )

    send(
        f"User {player} has joined room room:{room} at position 0", room=f"room:{room}"
    )


@socketio.on("leave", namespace="/game")
def leave(message):
    app.logger.info("leaving room")
    room, player = message["room"], message["player"]

    positions = get_room_positions_om(room)
    emit("update", {"positions": list(positions)}, room=f"room:{room}")

    # remove the Position key
    position = Position.find(
        (Position.player == player) & (Position.room == room)
    ).first()
    last_pos = position.pos
    Position.delete(position.pk)

    om_redis_conn.xadd(
        f"stream:{room}",
        {"event": EventType.LEAVE, "player": player, "room": room, "pos": last_pos},
    )

    # disconnect
    disconnect()

    # delete the room if there are no players left in the room
    # find any remaining players in the room
    remaining_players = Position.find(Position.room == room).all()
    if not remaining_players:
        app.logger.info("Closing room")

        # close the room
        close_room(f"room:{room}")

        # get the room key and delete it
        om_room = Room.find(Room.room == room).first()
        Room.delete(om_room.pk)
        app.logger.info("Room deleted")

        om_redis_conn.xadd(
            f"stream:{room}",
            {"event": EventType.END, "player": player, "room": room, "pos": last_pos},
        )
