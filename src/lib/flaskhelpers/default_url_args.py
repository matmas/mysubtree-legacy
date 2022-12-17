from flask import url_for


def init(app):
    app.jinja_env.globals["url"] = url


_default_url_args = {}


def set(arg, value):
    _default_url_args[arg] = value


def url(endpoint, **params):
    # hide unnecessary default values:
    for param, default in _default_url_args.items():
        if param in params and params[param] == default:
            del params[param]
    
    return url_for(endpoint, **params)
