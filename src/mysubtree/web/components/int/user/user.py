from hashlib import md5
from flask import url_for, request
from lib.html import Html
from lib import utils
from lib.base57 import base_encode
from mysubtree.backend import common
from mysubtree.backend.models.node.types.all import get_model

def user(user_, username, lang):
    html = Html()
    if user_:
        with html.a(
            href=url_for("node", lang=lang, nodetype="users", nid=base_encode(user_), slug=utils.slugify(username), type=get_model("users").branching()[0]),
            class_="user",
            component=True,
            **{"data-user": base_encode(user_)} # for live for getting current user
        ):
            #size = 14
            #html.img(class_="identicon", src=url_for('identicon', md5hash=md5(str(user_) + 'salt_1Dmmg-s3D0ver2s/d9sV ').hexdigest(), size=size), width=size, height=size)
            html.text(username or base_encode(user_))
    return html
