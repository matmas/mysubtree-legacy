#autoimport
from flask import abort, request, Markup, make_response
from flask.ext.babel import gettext as _
from lib.num import num
from mysubtree.backend import backend
from mysubtree.web.app import app
from mysubtree.web.templating import render_template
from mysubtree.web.components.int.node.node import node_list
from mysubtree.web.babel import set_locale
from mysubtree.web.user import get_user_node


@app.route("/<lang>/problematic")
def problematic(lang):
    set_locale(lang)
    nodelist = backend.get_problematic(get_user_node(), offset=num(request.args.get("offset", 0)))
    nodes_html = node_list(nodelist, view_options={
        "indicate_parent": _("under"),
        "hide_branching": True
    })
    if request.is_xhr:  # AJAX
        return make_response(unicode(nodes_html))
    nodes_html = Markup(nodes_html)
    return render_template("int/routes/node/nodelist/nodelist.html", lang=lang, name=_("problematic"), nodes_html=nodes_html)