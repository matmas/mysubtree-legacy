from urlparse import urlparse
from flask import url_for, Markup
from flask.ext.babel import format_datetime, gettext as _
from lib.html import Html
from mysubtree.web.templatefilters import activity_level, timesince
from mysubtree.backend.models.node.types.all import get_model
from .rename.rename import rename
from .icon.icon import icon
from ..branching.branching import branching_link

def title(node):
    html = Html()
#    url = urlparse(node.title())
#    if url.scheme in ["http", "https"] and url.netloc != "":
#        href = node.title()
#        rel = "nofollow"
    
    with html.span(class_=["title", "type", node.type], component=True):
        with html.span(
            class_=[
                "type",
                node.type,
                activity_level(node.created),
            ],
            title="%(type)s, %(created)s %(ago)s (%(exactly)s)" % {
                "type": get_model(node.type).type_long_name(),
                "created": _("created"),
                "ago": timesince(node.created),
                "exactly": format_datetime(node.created)},
        ):
            with html.span(class_="icon", style=("background: url(%s) no-repeat" % node.icon) if node.get("icon") else ""):
                pass
        with html.h1():
            html.text(node.title())
        html.add(rename(node))
        html.add(icon(node))
    return html
