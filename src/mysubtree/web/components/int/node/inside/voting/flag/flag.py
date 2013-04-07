from flask import url_for
from lib.html import Html
from flaskext.babel import gettext as _

def flag(node):
    html = Html()
    if node.is_flaggable_by_current_user():
        with html.a(
            href=url_for("flag", nid=node.nid()),
            class_=["flag", "problematic" if node.is_problematic() else ""],
            title=_("report problem"),
        ):
            pass
    return html
