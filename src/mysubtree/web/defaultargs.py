#autoimport
# Support for default url arguments
from lib.flaskhelpers import default_url_args
from mysubtree.web.app import app

default_url_args.init(app)
default_url_args.set("sort", "newest")
default_url_args.set("offset", 0)