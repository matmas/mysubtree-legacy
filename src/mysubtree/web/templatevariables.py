#autoimport
from flask_wtf import Form
from lib.base57 import base_encode
from lib.redirectback import get_back_url
from mysubtree.web.app import app
from mysubtree.backend.models.node.types.all import get_model
from mysubtree.web import user
from mysubtree.backend import common
from mysubtree.web.components.int.user.user import user as user_component

app.jinja_env.globals["enumerate"] = enumerate
app.jinja_env.globals["common"] = common
app.jinja_env.globals["user"] = user # breadcrumb, account
app.jinja_env.globals["user_component"] = user_component # account
app.jinja_env.globals["base_encode"] = base_encode # e.g. in breadcrumb
app.jinja_env.globals["get_model"] = get_model
app.jinja_env.globals["Form"] = Form
app.jinja_env.globals["get_back_url"] = get_back_url