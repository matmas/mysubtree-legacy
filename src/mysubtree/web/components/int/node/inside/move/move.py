from flask import url_for
from flask.ext.babel import gettext as _
from lib.html import Html

def move(node):
    html = Html()
    if node.is_movable_by_current_user():
        with html.a(
            class_="move",
            href=url_for('move', nid=node.nid()),
            title=_("move")
        ):
            pass
    return html