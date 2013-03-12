from lib.html import Html
from lib.base57 import base_encode
from flask import Markup, url_for
from flaskext.babel import gettext as _
from mysubtree.web.templatefilters import content_gettext as __

def parent(node, indicate_parent=False):
    html = Html()
    if indicate_parent and node.path:
        with html.span(class_="parent"):
            link = Markup('<a href="%s">%s</a>' % (
                url_for("node", lang=node.lang, nparent=base_encode(node.path[-1]["parent"]), nid=node.nparent(), slug=node.path[-1]["slug"]),
                __(node.path[-1]["short_name"])
            ))
            if isinstance(indicate_parent, basestring):
                html.text(Markup("(%s %s)" % (indicate_parent, link)))
            else:
                html.text(Markup("(%s)" % link))
    return html