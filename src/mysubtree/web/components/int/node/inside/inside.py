from flask import g, Markup
from lib.html import Html
from mysubtree.backend.node_ordering import correct_sort_type
from mysubtree.web.templatefilters import activity_level
from mysubtree.web.components.int.user.user import user
from .title.title import title
from .branching.branching import branching
from .parent.parent import parent
from .timesince.timesince import timesince
from .voting.like.like import like
from .voting.flag.flag import flag
from .delete.delete import delete
from .body.body import body
from .move.move import move
from .permalink.permalink import permalink

def inside(node, nodelist=None, nodelists=None, level=None, view_options=None):
    view_options = view_options or {}
    
    current_nodelist = nodelists[level] if nodelists else None
    sort = correct_sort_type(current_nodelist.get("sort") if current_nodelist else None)
    
    html = Html()
    html.add(like(node, sort))
    with html.td(class_="td-n"):
        with html.a(name=node.nid()): # anchor for focusing
            pass
        
        with html.div(
            class_=[
                "inside-inside",
            ],
        ):
            with html.div(class_="node-top"):
                html.add(title(node))
                html.add(body(node, view_options.get("body_should_expand")))
                html.add(parent(node, view_options.get("indicate_parent")))
                with html.span(class_="node-info"):
                    if not view_options.get("forbid_move"):
                        html.add(move(node))
                    if not view_options.get("forbid_delete"):
                        html.add(delete(node))
                    if not view_options.get("forbid_flag"):
                        html.add(flag(node))
                    if not node.hide_user_and_time():
                        html.add(timesince(node))
                        if not node.user and node.type == "votes":
                            html.text(node.ipaddress)
                        else:
                            html.add(user(node.user, node.username, node.nickname, node.lang))
                    html.add(permalink(node))
            if not view_options.get("hide_branching"):
                html.add(branching(node, nodelist, nodelists=nodelists, level=level))
    return html
