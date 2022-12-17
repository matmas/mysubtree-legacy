import os
import time
from .client import MarkdownClient, ConnectionLostException
from lib import process


def _run_server():
    process.run_in_background(["/usr/bin/env", "node", "%s/server.js" % os.path.dirname(__file__)])


def _ensure_server_running_and_connect_to_it(client):
    _run_server()
    for i in range(300):  # 30 seconds timeout
        if client.connect():
            break
        time.sleep(0.1)  # 100ms
    if not client.connected:
        raise Exception("Could not start markdown/server.js")


_client = MarkdownClient("localhost", 8124)


def to_html(text):
    if not _client.connected:
        _ensure_server_running_and_connect_to_it(_client)
    try:
        html = _client.get_html(text)
    except ConnectionLostException:
        _ensure_server_running_and_connect_to_it(_client)
        html = _client.get_html(text)
    return html


