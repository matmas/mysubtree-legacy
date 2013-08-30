#!../env/bin/python
# -*- coding: utf-8 -*-s
from os.path import dirname
from flask import Flask
from mysubtree import config

# create the application object
app = Flask(__name__)

#print "\n".join(dir(app))

app.config.update(
    APP_NAME = "Mysubtree",
    SLOGAN = "Be heard and not forgotten",
    SECRET_KEY = 'WO#i3zhmz@hOOf(oYsMhnXEyNN_McjSsM#E58L6S6ee=ST^RmE',
    MAX_CONTENT_LENGTH = 10 * 1024, # in bytes, for file uploads and normal POST submissions
    NUM_NODES_PER_PAGE = 10,
    TRUSTED_REFERER_NETLOC = "www.mysubtree.org",
    BASE_URL = "https://www.mysubtree.org"
)
