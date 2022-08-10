import os

from flask import Flask
import redis

app = Flask(__name__)

try:
    r = redis.Redis(
        host=os.environ.get("REDIS_HOST", "redis"),
        port=6379,
    )
except:
    pass

@app.route("/foo")
def hello_world():
    foo = r.get('foo')
    foo = "unset" if foo == None else foo.decode('utf-8')
    return f"<b>foo</b> is <b>{ foo }</b>"


@app.route("/set/<path:path>", methods=['POST'])
def set_foo(path):
    r.set('foo', path)
    val = r.get('foo').decode()
    return f"<b>foo</b> is now <b>{ val }</b>"


@app.route("/unset", methods=['DELETE'])
def unset_foo():
    r.delete('foo')
    return "<b>foo</b> has been deleted"

@app.route("/api/status/")
def status():
    return "OK"
