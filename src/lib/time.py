from datetime import datetime, timedelta

_delta = timedelta(0)

def utcnow():
    return datetime.utcnow() + _delta

def move_forward(**kwargs):
    global _delta
    _delta += timedelta(**kwargs)

def move_backward(**kwargs):
    global _delta
    _delta -= timedelta(**kwargs)
