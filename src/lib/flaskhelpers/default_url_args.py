from flask import request, url_for

def init(app):
    app.jinja_env.globals["url"] = url
    #app.jinja_env.globals["url_self"] = url_self
    #app.jinja_env.globals["args"] = args

_default_url_args = {}

def set(arg, value):
    _default_url_args[arg] = value
    
def url(endpoint, **params):
    # hide unnecessary default values:
    for param, default in _default_url_args.items():
        if param in params and params[param] == default:
            del params[param]
    
    return url_for(endpoint, **params)

#def url_self(**params):
    #return url(request.endpoint, **dict(request.view_args, **params))

#def args(arg):
    #return request.args.get(arg, _default_url_args[arg])
