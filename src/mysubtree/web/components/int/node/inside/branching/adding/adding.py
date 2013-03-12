from flask import Markup, url_for, session
from flaskext.babel import gettext as _
from lib.html import Html
from lib.base57 import base_decode
from lib.flaskhelpers.default_url_args import url
from mysubtree.backend import common
from mysubtree.backend.models.node.types.all import get_model
from mysubtree.web.user import get_user, get_user_node

def adding(node):
    html = Html()
    if node.is_addable_to_by_current_user():
        types = node.types_in_menu()
        if len(types) > 0:
            with html.a(
                class_="add",
                title=_("add"),
                href=url_for("post", nparent=node.nparent(), nid=node.nid()),
            ):
                html.text(Markup("&nbsp;"))
            
            #with html.div(
                #class_=["menu", "attach"],
                #title=_("add"),
            #):
                #html.text(Markup("&nbsp;"))
                #with html.ul():
                    #for type in types:
                        #with html.li():
                            #with html.a(
                                #href=url_for("post", nparent=node.nparent(), nid=node.nid(), type=type),
                                #class_=["add", "type", type],
                                #**{"data-type": type}
                            #):
                                #with html.span(class_="icon"):
                                    #pass
                                #html.text(get_model(type).str_new_type())
            with html.span(
                class_=["paste"] + types,
                title=_("move it here"),
                component=True,
                **{"data-url": url_for("move_to", nid=node.nid(), nparent=node.nparent())}
            ):
                pass
            
            moving_node = session.get("moving_node", {})
            moving_node_type = moving_node.get("type")
            moving_node_id = base_decode(moving_node.get("nid"))
            moving_node_parent = base_decode(moving_node.get("nparent"))
            if moving_node_type in types and moving_node_parent != node.id and moving_node_id != node.id and moving_node_id not in [ancestor["id"] for ancestor in node.path]:
                with html.a(
                    href=url_for("move_to", nid=node.nid(), nparent=node.nparent()),
                    class_=["paste-now"],
                    title=_("move it here"),
                ):
                    pass
    return html
