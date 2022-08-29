---
title: Redis Light, Green Light
published: false
description: My submission to the Redis Hackathon on DEV!
tags: redishackathon, redis, flask, socketio
---

### Overview of My Submission

I recreated the game "Red Light, Green Light" using Python, TypeScript and Redis!

One day in early August I was browsing DEV while re-watching MrBeast's Squid Game recreation video in the background when I cam across the DEV article about the Redis Hackathon. Then I got a crazy idea: **Redis Light, Green Light**! I became determined to create my own online, real-time, multi-player version of Red Light, Green Light powered by Redis and submit it to the Wacky Wildcard project category for my chance to win the hackathon!

I used my favorite languages and frameworks for rapid prototyping: Python with Flask to power the backend and TypeScript with the Nuxt.js framework to build the frontend components for my game.

For real-time communication I added the `Flask-SocketIO` library to my Flask app and the `socket.io-client` library to my Nuxt app. I also added celery for scheduling and processing async tasks. Redis was used as the message queue for websocket messages and it was also used as the broker for celery tasks.

This was my first project working with Redis Stack and Redis OM and I really liked using these tools. I stored most of my data in hashes, and the Redis OM library is perfect for using this data type. I also used Redis streams for the first time which was a lot of fun.

The backend application services include:

- Flask server (for API endpoints and Websocket handlers)
- Celery beat task scheduler (for scheduling tasks to change the light color in each room)
- Celery worker (to change the light color for a room and to update that players in that room via Websocket)

![Project Diagram](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/0egpm1igfqyon5kjtujv.png)

Please check out the video below for more details about how the project works.

### Submission Category

Wacky Wildcards

### Redis Light, Green Light YouTube Video

{ % youtube BoalZKmgoEU %}

### Language Used

Python. Honorable mention for JavaScript.

### Link to Code

{% embed https://github.com/briancaffey/redis-light-green-light-dev-to-hackathon %}

### Additional Resources / Info

![Redis Light, Green Light](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/m3rqy7eqz40nqk1e04jj.png)

![Redis Light, Green Light gameplay](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/wkmgiz8wtq484rn6dmfc.png)

- - -

* _Check out [Redis OM](https://redis.io/docs/stack/get-started/clients/#high-level-client-libraries), client libraries for working with Redis as a multi-model database._
* _Use [RedisInsight](https://redis.info/redisinsight) to visualize your data in Redis._
* _Sign up for a [free Redis database](https://redis.info/try-free-dev-to)._
