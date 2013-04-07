from flask import url_for
from flaskext.babel import gettext as _
from lib.html import Html

def rename(node):
    html = Html()
    if node.is_renameable_by_current_user():
        with html.a(
            class_="rename",
            href=url_for("rename", lang=node.lang, nid=node.nid()),
            title=_("rename"),
        ):
            pass
    return html