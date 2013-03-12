from flask import Markup, url_for
from flaskext.babel import gettext as _
from mysubtree.backend import common
from mysubtree.backend.models.node.types.all import get_model
from lib.html import Html

def delete(node):
    html = Html()
    if node.is_deletable_by_current_user():
        with html.a(
            href=url_for('delete', nparent=node.nparent(), nid=node.nid()),
            class_="delete",
            title=_("delete"),
        ):
            pass
    if node.is_restorable_by_current_user():
        with html.a(
            href=url_for('restore', nparent=node.nparent(), nid=node.nid()),
            class_="restore",
            title=_("restore"),
        ):
            pass
    return html