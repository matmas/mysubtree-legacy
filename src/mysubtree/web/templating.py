#autoimport
import os
import inspect
import flask
from flask import Markup, request
from mysubtree.web.app import app

def render_template(path, **kwargs):
    root_dir = os.path.dirname(__file__) + "/components/"
    caller_file = inspect.stack()[1][1]
    app.jinja_loader.searchpath = [
        root_dir, # from components
        os.path.dirname(caller_file), # from caller
    ]
    return flask.render_template(path, **kwargs)

def _render_template_install():
    # a bit of monkey-patching
    old_get_source = flask.templating.DispatchingJinjaLoader.get_source
    def get_source(self, environment, template):
        source = old_get_source(self, environment, template)
        filename = source[1]
        app.jinja_loader.searchpath.append(os.path.dirname(filename)) # from template (works also from within other templates)
        return source
    flask.templating.DispatchingJinjaLoader.get_source = get_source

_render_template_install()

