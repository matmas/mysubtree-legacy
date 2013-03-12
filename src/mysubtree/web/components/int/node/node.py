from flask import request, session
from lib.html import Html
from mysubtree.backend import backend
from .inside.inside import inside
from .paging.paging import paging
from .sorting.sorting import sorting
from mysubtree.backend import common

def node_component(node, nodelist=None, nodelists=None, level=None,
        view_options=None, # for this node and subnodes recursively
        view_options_for_node=None, # only for this node
        view_options_for_subnodes=None): # only for subnodes
    view_options = view_options or {}
    view_options_for_node = view_options_for_node or {}
    view_options_for_subnodes = view_options_for_subnodes or {}
    view_options_for_node = dict(view_options_for_node, **view_options) # to have relevant options together
    nodelist_type = nodelist.get("type") if nodelist else None
    
    html = Html()
    with html.tbody(
        class_=["node", "moving-node" if session.get("moving_node", {}).get("nid") == node.nid() else ""],
        component=True,
        **{
            "data-type": node.type,
        }
    ):
        with html.tr(
            class_=[
                "inside",
                "live",
                "reading" if view_options_for_node.get("indicate_reading") and node.is_just_being_read() else "",
            ],
            id=node.nid(),
            component=True,
        ):
            html.add(inside(node, nodelist, nodelists=nodelists, level=level, view_options=dict(view_options_for_node, expanded_type=nodelist_type)))
        with html.tr(class_="tr-c"):
            with html.td(
                class_=[
                    "type-container",
                    "fill" if level and level % 2 == 1 else "", # in branching is similar class
                ],
                colspan="2",
                component=True,
            ):
                with html.div(class_="add-container", component=True, lazy=True):
                    pass
                with html.div(
                    class_="nodelist",
                    component=True,
                    **{"data-type": nodelist_type or ""} # for branching to know that this type is expanded
                ):
                    if nodelist: # expanded
                        html.add(node_list(nodelist, nodelists=nodelists, level=level + 1, node=node, view_options=dict(view_options, **view_options_for_subnodes)))
    return html


def node_list(nodelist, node=None, nodelists=None, level=None, view_options=None):
    html = Html()
    if nodelist["nodes_count"] > 0:
        with html.div(class_="node-list"):
            nodes_type = nodelist.get("type")
            if node and nodes_type:
                html.add(sorting(node, nodelist, nodelists, level))
            with html.table(class_="nodes", component=True):
                for subnode in nodelist["nodes"]:
                    subnodelist = None
                    if nodelists and level + 1 < len(nodelists) and nodelists[level + 1]["nodes"][0].parent == subnode.id:
                        subnodelist = nodelists[level + 1]
                    html.add(node_component(subnode, subnodelist, nodelists=nodelists, level=level, view_options=view_options))
            html.add(paging(node, nodelist, nodelists, level))
    return html