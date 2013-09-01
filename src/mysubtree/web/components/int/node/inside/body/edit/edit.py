from flask import url_for, request
from flask.ext.babel import gettext as _
from lib.html import Html

def edit(node):
    html = Html()
    if node.is_editable_by_current_user():
        with html.a(
            href=url_for("edit", lang=node.lang or request.view_args["lang"], nid=node.nid()),
            class_="edit",
            title=_("edit")
        ):
            pass
    if node.is_edit_suggestable_by_current_user():
        with html.a(
            href=url_for("edit", lang=node.lang or request.view_args["lang"], nid=node.nid()),
            #href=url_for("post", type="edit-suggestions", nid=node.nid()),
            class_="edit suggest",
            title=_("suggest edit"),
        ):
            pass
    return html
