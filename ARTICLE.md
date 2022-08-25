---
title: Redis Light, Green Light
published: false
description: My submission to the Redis Hackathon on DEV!
tags: redishackathon, redis, flask, socketio
---

### Overview of My Submission

I recreated the game "Red Light, Green Light" using Python, TypeScript and Redis!

One day in early August I was browsing Dev.to while re-watching MrBeast's Squid Game recreation video in the background when I cam across the DEV article about the Redis Hackathon. Then I got a crazy idea: **Redis Light, Green Light**! I became determined to create my own online, real-time, multi-player version of Red Light, Green Light powered by Redis and submit it to the Wacky Wildcard project category for my chance to win the hackathon!

I used my favorite languages and frameworks for rapid prototyping: Python with Flask to power the backend and TypeScript with the Nuxt.js framework to build the frontend components for my game.

For real-time communication I added the `Flask-SocketIO` library to my Flask app and the `socket.io-client` library to my Nuxt app. I also added celery for scheduling and processing async tasks (more on this later). Redis was used as the message queue for websocket messages and it was also used as the broker for celery tasks.

`redis-py` was used to get and set hash values that kept track of live game data in Redis. Redis streams were used as a way to track all events for a historical record of every action in every game.

Like I do with most of my projects, I used `docker-compose` to set up the backend application services and database and I used Nuxt's `npm run dev` command to work on the UI.

The backend application services include:

- Flask server (for API endpoints and Websocket handlers)
- Celery beat task scheduler (for scheduling tasks to change the light color in each room)
- Celery worker (to change the light color for a room and to update that players in that room via Websocket)

### Submission Category

Wacky Wildcards

### [Optional: Video Explainer of My Project]

[Note]: # (This is where you can embed the optional bonus video you created to accompany your submission. Ensure your video is published publicly to YouTube and you’ve used the embed tag here to share it with us. By opting to include a video, you will be eligible for BONUS prizes. Learn more in the announcement post.)

### Language Used

Python

### Link to Code

{% embed https://github.com/briancaffey/redis-light-green-light-dev-to-hackathon %}

### Additional Resources / Info

[Note:] # Screenshots/demo videos are encouraged!

- - -

* _Check out [Redis OM](https://redis.io/docs/stack/get-started/clients/#high-level-client-libraries), client libraries for working with Redis as a multi-model database._
* _Use [RedisInsight](https://redis.info/redisinsight) to visualize your data in Redis._
* _Sign up for a [free Redis database](https://redis.info/try-free-dev-to)._
