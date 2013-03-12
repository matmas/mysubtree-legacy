#autoimport
from mysubtree.web.app import app
from mysubtree import config
from os.path import dirname

max_content_length = app.config["MAX_CONTENT_LENGTH"]

if config.debug:
    with open(dirname(__file__) + "/max_content_length.js", "w") as f:
        f.write("var MAX_CONTENT_LENGTH = %s;" % max_content_length)