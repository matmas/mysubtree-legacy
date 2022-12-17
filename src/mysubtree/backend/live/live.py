import os
import time
from .client import Client, ConnectionLostException
from lib import process
from lib.base57 import base_encode
from flask import g
from lib.json import json

_live_enabled = False
_client = Client("localhost", 8125)

def enable_live():
    global _live_enabled
    _live_enabled = True
    _ensure_server_running_and_connect_to_it(_client)


def _run_server():
    process.run_in_background(["/usr/bin/env", "coffee", "%s/live_server/live_server.coffee" % os.path.dirname(__file__)])


def _ensure_server_running_and_connect_to_it(client):
    _run_server()
    for i in range(300): # 30 seconds timeout
        if client.connect():
            break
        time.sleep(0.1) # 100ms
    if not client.connected:
        raise Exception("Could not start live server")


def send(text):
    if not _client.connected:
        _ensure_server_running_and_connect_to_it(_client)
    try:
        _client.send(text)
    except ConnectionLostException:
        _ensure_server_running_and_connect_to_it(_client)
        _client.send(text)

#===============================================================================


from mysubtree.web.app import app

@app.before_request
def before_request():
    g.changed = []
    g.appeared = []
    g.disappeared = []
    g.notifications = []

@app.after_request
def after_request(response):
    if g.changed or g.appeared or g.disappeared or g.notifications:
        if _live_enabled:
            send(json.dumps({
                "changed": g.changed,
                "appeared": g.appeared,
                "disappeared": g.disappeared,
                "notifications": g.notifications,
            }))
    return response

#===============================================================================


def on_node_insert(node):
    record = {
        "url": node.url(whole=True),
        "nid": node.nid(),
        "nparent": node.nparent(),
        "type": node.type,
    }
    if record not in g.appeared:
        g.appeared.append(record)


def on_node_update(id):
    nid = base_encode(id)
    try:
        if nid not in g.changed:
            g.changed.append(nid)
    except RuntimeError: # working outside of request context
        pass


def on_notifications(user):
    if user not in g.notifications:
        g.notifications.append(base_encode(user))


def on_new_response(user):
    on_notifications(user)


def on_seeing_response(user):
    on_notifications(user)
    

def on_problematic_num_change(user_or_moderator):
    on_notifications(user_or_moderator)


def on_node_move(node):
    nid = node.nid()
    if nid not in g.disappeared:
        g.disappeared.append(nid)
    
    record = {
        "nid": node.nid(),
        "nparent": node.nparent(),
        "type": node.type,
    }
    if record not in g.appeared:
        g.appeared.append(record)
