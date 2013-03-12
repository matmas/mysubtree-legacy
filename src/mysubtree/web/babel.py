#autoimport
from flask import g, request
from .app import app

from flaskext.babel import Babel
babel = Babel(app)

def set_locale(locale):
    if getattr(g, "_get_locale_called", None):
        raise Exception("set_locale must be called before any use of gettext functions or never")
    g.locale = locale

def get_browser_locale():
    locale = request.accept_languages.best_match(["sk", "sk-sk", "en"])
    if locale == "sk-sk": # iPhone sends sk-sk
        locale = "sk"
    return locale 

@babel.localeselector
def _get_locale():
    g._get_locale_called = True
    locale = getattr(g, "locale", None)
    if not locale:
        locale = request.args.get("lang")
    return locale

#TODO:
#@babel.timezoneselector
#def get_timezone():
    #user = getattr(g, 'user', None)
    #if user is not None:
        #return user.timezone
        
#from flask import request
