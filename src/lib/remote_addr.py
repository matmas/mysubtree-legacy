from flask import request


def remote_addr():
    ip = request.headers.get("X-Real-IP")
    if not ip:
        ip = request.remote_addr
    return ip