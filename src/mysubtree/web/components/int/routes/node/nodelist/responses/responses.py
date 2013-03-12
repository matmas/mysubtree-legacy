#autoimport
from flask import abort, request, Markup, make_response
from flaskext.babel import gettext as _
from lib.num import num
from mysubtree.backend import backend
from mysubtree.web.app import app
from mysubtree.web.templating import render_template
from mysubtree.web.components.int.node.node import node_list
from mysubtree.web.babel import set_locale


@app.route("/<lang>/responses")
def responses(lang):
    set_locale(lang)
    nodelist = backend.get_responses_of_current_user(offset=num(request.args.get("offset", 0)))
    nodes_html = node_list(nodelist, view_options={
        "indicate_parent": _("to"),
        "indicate_reading": True,
        "hide_branching": True,
        "forbid_delete": True, # because user might think he or she is just deleting the message from his or her inbox
        "forbid_move": True,
    })
    if request.is_xhr: # AJAX
        return make_response(unicode(nodes_html))
    nodes_html = Markup(nodes_html)
    return render_template("int/routes/node/nodelist/nodelist.html", lang=lang, name=_("responses"), nodes_html=nodes_html)