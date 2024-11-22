#autoimport
import logging
import re
from flask import request, redirect, Markup, make_response, abort, url_for, session
from flask.ext.babel import gettext as _
from lib.flaskhelpers.default_url_args import url
from lib.base57 import base_encode, base_decode
from lib.num import num
from mysubtree.backend import backend
from mysubtree.backend.node_ordering import correct_sort_type
from mysubtree.backend.models.node.types.root import Root
from mysubtree.db import get_root_id
from mysubtree.web.app import app
from mysubtree.web.templating import render_template
from mysubtree.web.babel import set_locale
from mysubtree.web.components.int.node.inside.inside import inside as node_inside
from mysubtree.web.components.int.node.node import node_list
from mysubtree.web.components.int.node.node import node_component
from mysubtree.web.o import parse_o
from mysubtree.web.user import get_user
from mysubtree.web.cache import cache

def should_not_cache():
    if app.config['TESTING']:
        return True
    if get_user():
        return True
    if session:
        return True
    return False

@app.route("/en", defaults={"lang": "en"})
@app.route("/sk", defaults={"lang": "sk"})
@app.route("/languages/<lang>")
def language_root(lang):
    return redirect(url_for("node", lang=lang, nid=base_encode(get_root_id(lang)), type=Root.branching()[0]))


@app.route("/en/root",                                      defaults={"nodetype": "root", "nid": "en", "lang": "en"})
@app.route("/en/root/<type>",                               defaults={"nodetype": "root", "nid": "en", "lang": "en"})
@app.route("/sk/root",                                      defaults={"nodetype": "root", "nid": "sk", "lang": "sk"})
@app.route("/sk/root/<type>",                               defaults={"nodetype": "root", "nid": "sk", "lang": "sk"})

@app.route("/<lang>/users/<alias>",                         defaults={"nodetype": "users", "nid": None})
@app.route("/<lang>/users/<alias>/<type>",                  defaults={"nodetype": "users", "nid": None})

# without the url convertor nid will contain part of the multi-word slug until the last dash
@app.route("/<lang>/items/<alphanum:nid>",                  defaults={"nodetype": "items"})
@app.route("/<lang>/items/<alphanum:nid>/<type>",           defaults={"nodetype": "items"})
@app.route("/<lang>/items/<alphanum:nid>-<slug>",           defaults={"nodetype": "items"})
@app.route("/<lang>/items/<alphanum:nid>-<slug>/<type>",    defaults={"nodetype": "items"})

@app.route("/<lang>/comments/<nid>",                        defaults={"nodetype": "comments"})
@app.route("/<lang>/comments/<nid>/<type>",                 defaults={"nodetype": "comments"})
@app.route("/<lang>/edit-suggestions/<nid>",                defaults={"nodetype": "edit-suggestions"})
@app.route("/<lang>/edit-suggestions/<nid>/<type>",         defaults={"nodetype": "edit-suggestions"})
@app.route("/<lang>/log-entries/<nid>",                     defaults={"nodetype": "log-entries"})
@app.route("/<lang>/log-entries/<nid>/<type>",              defaults={"nodetype": "log-entries"})
@app.route("/<lang>/trash/<nid>",                           defaults={"nodetype": "trash"})
@app.route("/<lang>/trash/<nid>/<type>",                    defaults={"nodetype": "trash"})
@app.route("/<lang>/versions/<nid>",                        defaults={"nodetype": "versions"})
@app.route("/<lang>/versions/<nid>/<type>",                 defaults={"nodetype": "versions"})
@app.route("/<lang>/votes/<nid>",                           defaults={"nodetype": "votes"})
@app.route("/<lang>/votes/<nid>/<type>",                    defaults={"nodetype": "votes"})

@cache.cached(timeout=60, unless=should_not_cache)
def node(lang, nodetype, nid, type=None, slug=None, alias=None):
    if nodetype == "users":
        node = backend.get_node_from_alias(alias) or abort(404)
    else:
        if not nid:
            nid = base_encode(get_root_id(lang))
        node = backend.get_node_from(nid) or abort(404)
    set_locale(node.lang or lang)
    sort = correct_sort_type(request.args.get("sort"))
    if nodetype != "users":
        if not request.is_xhr: # not AJAX
            if node.slug() != slug or node.lang and node.lang != lang:
                return redirect(url("node", nodetype=node.type, lang=node.lang, nid=node.nid(), slug=node.slug(), type=type, sort=sort, o=request.args.get("o")))  #, code=301
        
    backend.getting_nodes_below(node)
    if type:
        nodelist = backend.get_nodes(node.id, node.type, type, sort=sort, offset=num(request.args.get("offset", 0)))
        nodelist["nodes_count"] = node.count(type)
    else:
        nodelist = {"nodes": [], "nodes_count": 0, "offset": 0}
    
    node_type = node.type
    view_options = {"hide_branching": True, "indicate_parent": _("under")} if node_type == "users" else {}
    
    if request.is_xhr: # AJAX
        if not type:
            if request.args.get("whole"): # for appearing nodes with live
                return make_response(unicode(node_component(node)))
            else:
                return make_response(unicode(node_inside(node)))
        else:
            return make_response(unicode(node_list(nodelist, node=node, view_options=view_options)))
    
    canonical_url = request.url_root.rstrip('/') + node.url(type=type, offset=nodelist["offset"])
    
    nodelists = []
    if nodelist["nodes"]:
        nodelists = [nodelist]
    
    for i, o in enumerate(parse_o(request.args.get("o"))):
        sort = o.get("sort") or "newest"
        offset = o.get("offset") or 0
        if i == 0:
            node_type = node.type
            node_parent = node.parent
            node_id = node.id
        else:
            node_type = first_node.parent_type
            node_parent = first_node.parent_of_parent
            node_id = first_node.parent
        
        if node_type == "root":
            break
        
        nodelist = backend.get_nodes(node_parent, None, node_type, sort, offset)
        
        try:
            this_node = (node_of_parent for node_of_parent in nodelist["nodes"] if node_of_parent.id == node_id).next()
            if nodelists:
                nodelists[-1]["node"] = this_node
                nodelists[-1]["nodes_count"] = this_node.count(nodelists[-1]["type"])
        except StopIteration: # in the middle of move - not propagated yet
            nodelist = nodelists[-1] # last good one
            break # cut it there
        
        first_node = nodelist["nodes"][0]
        node = None
        nodelists.append(nodelist)
    if not node:
        node = backend.get_node(first_node.parent) or abort(404)
        nodelists[-1]["node"] = node
        nodelists[-1]["nodes_count"] = node.count(nodelists[-1]["type"])
        
    nodelists = list(reversed(nodelists)) # we need to begin with the outermost list
    node_html = Markup(node_component(node, nodelist, nodelists=nodelists, level=-1, view_options_for_node={"body_should_expand": True}, view_options_for_subnodes=view_options))
    return render_template("node.html", node=node, canonical_url=canonical_url, lang=lang, node_html=node_html)
