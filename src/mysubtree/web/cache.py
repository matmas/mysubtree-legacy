from flask.ext.cache import Cache
from .app import app

cache = Cache(app)