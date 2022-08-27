# Redis Light, Green Light

An online multiplayer implementation of the game "Red Light, Green Light" using Redis and Flask. This is my submission for the 2022 [Redis Hackathon on DEV](https://dev.to/devteam/announcing-the-redis-hackathon-on-dev-3248)

[Insert app screenshots](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#uploading-assets)

# Overview video (Optional)

Here's a short video that explains the project and how it uses Redis:

[Insert your own video here, and remove the one below]

[![Embed your YouTube video](https://i.ytimg.com/vi/vyxdC1qK4NE/maxresdefault.jpg)](https://www.youtube.com/watch?v=vyxdC1qK4NE)

## How it works

### How the data is stored:

Real-time data for game state is stored in hashes called `Room` and `Position`:

```py
class Room(HashModel):
    room: uuid.UUID = Field(index=True)
    light: str # red or green
    changed: int # timestamp
    created: int # timestamp


class Position(HashModel):
    pos: int # represents how many steps a player has taken
    state: str # alive or dead
    player: uuid.UUID = Field(index=True)
    room: uuid.UUID = Field(index=True)
```

RedisOM is used to perform CRUD (create, read, update and delete) operations on these hashes in API requests, websocket handlers and celery tasks. Here are some examples:

**Creating a new room**

```py
room = Room(
    room=new_room_id, light=LightState.RED, changed=timestamp, created=timestamp
)
```

**Changing the color of a light for a room**

```py
om_room = Room.find(Room.room == room).first()
om_room.update(light=state, changed=timestamp)
```

In Squid Game, Jun-ho learns that the games have been running for over 30 years, and that his elder brother Hwang In-ho was the winner in 2015. To keep a permanent historical record all of the events from a room I use Redis streams and the `XADD` command.

There are eight types of events that can happen in the lifecycle of a game:

```py
class EventType:
    CREATED = "created"
    LIGHT = "light"
    JOIN = "join"
    MOVE = "move"
    WIN = "win"
    DIE = "die"
    LEAVE = "leave"
    END = "end"
```

Here are some examples of how I store game event data in streams:

**Record a room creation event**

```py
om_redis_conn.xadd(f"stream:room:{new_room_id}", {"event": EventType.CREATED})
```

**Record when a player moves successfully**

```py
om_redis_conn.xadd(
    f"stream:room:{room}",
    {
        "event": EventType.MOVE,
        "player": player,
        "pos": new_pos,
    },
)
```

**Record when a player wins**

```py
om_redis_conn.xadd(
    f"stream:room:{room}",
    {"event": EventType.WIN, "player": player, "pos": value},
)
```

### How the data is accessed:

Data is accessed using a combination of Redis OM queries and raw Redis commands. When a user joins a room, the web socket handler fetches all players currently in the give room with the following query:

```py
positions = Position.find(Position.room == room).all()
```

To display all events for a given room, the `XRANGE` command is used to fetch all events which are then sent back to the client:

```py
events = om_redis_conn.xrange(f"stream:room:{room}", min="-", max="+")
```

## How to run it locally?

Running the application in a local development environment involves starting the web client and also starting multiple backend services. Backend services can be brought up using a `docker-compose.yml` file or they can be started by running commands in Python virtual environment.

### Prerequisites

To run the client locally you will need:

- Node 16.16.0

To run the backend locally with docker and docker-compose you will need:

- docker 20.10.14+
- docker-compose 1.29.2

Recommended:

- Redis Insights

### Local installation

To start the backend services (Flask API, celery worker, celerybeat scheduler and Redis Stack), you can run:

```
docker-compose up
```

Make sure that you do not have any local instances of redis using port `6379` before running the above command, or it will fail to start.

To start the client, run the follow commands:

```
cd client
npm i
npm run dev
```

The backend can also be ran locally using virtual environments. You can run the `redis-stack` docker image with:

```
docker-compose -f redis-stack.yml up
```

Create a virtual environment in the `/app` directory and active it:

```
python3 -m venv .env
source .env/bin/activate
```

Then install pip requirements:

```
pip install -r requirements.txt
pip install -r requirements_dev.txt
```

Next you can start the three services in different windows. Before starting each service, make sure to activate the virtual environment with:

```
source .env/bin/activate
```

**Start the Flask API server**

```
gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 wsgi:app --reload
```

You should see:

```
[2022-08-27 11:19:29 -0400] [17881] [INFO] Starting gunicorn 20.1.0
[2022-08-27 11:19:29 -0400] [17881] [INFO] Listening at: http://127.0.0.1:8000 (17881)
[2022-08-27 11:19:29 -0400] [17881] [INFO] Using worker: geventwebsocket.gunicorn.workers.GeventWebSocketWorker
[2022-08-27 11:19:29 -0400] [17882] [INFO] Booting worker with pid: 17882
```

**Start the celery worker**

```
celery --app app.celery worker --loglevel=info
```

```
celery@Brians-MacBook-Pro.local v5.2.3 (dawn-chorus)

macOS-12.3.1-arm64-arm-64bit 2022-08-27 11:21:05

[config]
.> app:         app:0x105e63a30
.> transport:   redis://localhost:6379/2
.> results:     redis://localhost:6379/3
.> concurrency: 8 (prefork)
.> task events: OFF (enable -E to monitor tasks in this worker)

[queues]
.> celery           exchange=celery(direct) key=celery


[tasks]
  . update_light
  . update_lights

[2022-08-27 11:21:06,094: INFO/MainProcess] Connected to redis://localhost:6379/2
[2022-08-27 11:21:06,149: INFO/MainProcess] mingle: searching for neighbors
[2022-08-27 11:21:07,234: INFO/MainProcess] mingle: all alone
[2022-08-27 11:21:07,356: INFO/MainProcess] celery@Brians-MacBook-Pro.local ready.
```

**Start the celerybeat service**

```
celery --app app.celery beat --loglevel=info
```

You should see:

```
celery beat v5.2.3 (dawn-chorus) is starting.
__    -    ... __   -        _
LocalTime -> 2022-08-27 11:24:58
Configuration ->
    . broker -> redis://localhost:6379/2
    . loader -> celery.loaders.app.AppLoader
    . scheduler -> celery.beat.PersistentScheduler
    . db -> celerybeat-schedule
    . logfile -> [stderr]@%INFO
    . maxinterval -> 5.00 minutes (300s)
[2022-08-27 11:24:58,824: INFO/MainProcess] beat: Starting...
[2022-08-27 11:25:00,847: INFO/MainProcess] Scheduler: Sending due task update_lights (update_lights)
```

Before starting `celerybeat`, make sure that you have deleted a file called `celerybeat-schedule.db`.

The client runs on `http://localhost:3000`. It makes API and websocket connections with the backend which runs on `http://localhost:8000`.

## Deployment

To make deploys work, you need to create free account on [Redis Cloud](https://redis.info/try-free-dev-to)

### Google Cloud Run

[Insert Run on Google button](https://cloud.google.com/blog/products/serverless/introducing-cloud-run-button-click-to-deploy-your-git-repos-to-google-cloud)

### Heroku

[Insert Deploy on Heroku button](https://devcenter.heroku.com/articles/heroku-button)

### Netlify

[Insert Deploy on Netlify button](https://www.netlify.com/blog/2016/11/29/introducing-the-deploy-to-netlify-button/)

### Vercel

[Insert Deploy on Vercel button](https://vercel.com/docs/deploy-button)

