from flask import Markup, url_for
from lib.html import Html
from flask.ext.babel import gettext as _

def like(node, sort):
    html = Html()
    with html.td(class_="voting", component=True):
        if node.is_votable():
            with html.span(class_="vote-indicator", component=True):
                html.text(str(node.get_votes(sort)))
            if node.is_votable_by_current_user():
                with html.a(
                    href=node.url_for("vote"),
                    class_=["like", "button"],
                    component=True,
                    **{
                        "data-default":  "+",
                        "data-pressed": "&minus;",
                    }
                ):
                    html.text(Markup("+"))
    return html