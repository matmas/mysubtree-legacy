from flask import url_for
from flaskext.babel import gettext as _
from lib.html import Html

def icon(node):
    html = Html()
    if node.is_icon_changeable_by_current_user():
        with html.a(
            class_="seticon",
            href=url_for('icon', nid=node.nid()),
            title=_("set icon"),
        ):
            pass
    return html