# -*- coding: utf-8 -*-
from flask import request, Markup
from flask.ext.babel import gettext as _
from lib.base57 import base_encode
from lib.html import Html
from lib.flaskhelpers.default_url_args import url
from mysubtree.backend import common
from mysubtree.backend.node_ordering import correct_sort_type_of_subnodes
from mysubtree.backend.models.node.types.all import get_model
from mysubtree.web.templatefilters import timesince, activity_level
from mysubtree.web.o import compile_o
from .adding.adding import adding

def branching(node, nodelist=None, nodelists=None, level=None):
    html = Html()
    with html.div(class_="branching", component=True):
        branched = False
        for branching_type in node.branching():
            if not get_model(branching_type).is_auxiliary() or node.should_not_consider_auxiliary():
                if node.count(branching_type) > 0 or get_model(branching_type).always_show_type():
                    html.add(render_branching_type(branching_type, node, nodelist, nodelists, level))
                    branched = True
        if branched:
            html.text(Markup("&nbsp; &nbsp; "))
        html.add(adding(node))
        
        with html.div(class_="auxiliary"):
            for branching_type in node.branching():
                if get_model(branching_type).is_auxiliary() and not node.should_not_consider_auxiliary():
                    if node.count(branching_type) > 0 or get_model(branching_type).always_show_type():
                        html.add(render_branching_type(branching_type, node, nodelist, nodelists, level))
    return html

def render_branching_type(branching_type, node, nodelist=None, nodelists=None, level=None):
    html = Html()
    with branching_link(html, branching_type, node, nodelist, nodelists, level):
        count = node.count(branching_type)
        with html.span(class_="icon"):
            pass
        html.text(get_model(branching_type).type_name(count))
    html.text(Markup("&nbsp; "))
    return html

def branching_link(html, branching_type, node, nodelist=None, nodelists=None, level=None):
    lang = node.lang or request.view_args["lang"]
    sort = correct_sort_type_of_subnodes(nodelists[level].get("sort") if nodelists else None, node, branching_type) # when opening, allow to inherit sort from current nodelist
    
    nodelist_type = nodelist.get("type") if nodelist else None
    is_expanded = branching_type == nodelist_type
    
    if not is_expanded: # open
        o = compile_o(reversed(nodelists[:level+1])) if level >= 0 else None
        
        href = node.url(type=branching_type, sort=sort, o=o, _anchor=node.nid())
    else: # close
        o = compile_o(reversed(nodelists[:level])) if level >= 0 else None
        offset = nodelists[level].get("offset", 0) if nodelists else None
        
        if level == -1:
            parent_node = node # node stays the same
            type = None # type is closed
            href = node.url(nodetype=parent_node.type, nid=parent_node.nid(), slug=parent_node.slug(), type=type, sort=sort, offset=offset, o=o)
        else:
            #parent_node = nodelist["node"] # opened node moved upwards
            type = node.type
            href = node.url(nodetype=node.parent_type, nid=base_encode(node.parent), slug=node.path[-1]["slug"], type=type, sort=sort, offset=offset, o=o,
                _anchor=node.nid() # focus this node
            )
            
    
    return html.a(
        href=href,
        class_=[
            "branch",
            "type",
            "fill" if level and level % 2 == 1 else "fill2",  # in node_component is similar class
            branching_type,
            "expanded" if is_expanded else "",
            activity_level(node.get_activity(branching_type)),
        ],
        title=timesince(node.get_activity(branching_type), coarse=True, prefix=_("activity") + " "),
        **dict(
            {"rel": "nofollow"} if branching_type == "trash" else {},
            **{"data-type": branching_type}
        )
    )