from flask import url_for
from flask.ext.babel import gettext as _
from lib.html import Html

def accept(node):
    html = Html()
    if node.is_acceptable_by_current_user():
        with html.a(
            href=url_for('accept', nid=node.nid()),
            class_=["accept", "button"],
        ):
            html.text(_("accept"))
    return html
