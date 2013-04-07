from flask import Markup, request
from flaskext.babel import gettext as _
from lib.html import Html
from lib.flaskhelpers.default_url_args import url
from mysubtree.backend import common
from mysubtree.web.o import compile_o
from mysubtree.web.app import app

def paging(node, nodelist, nodelists, level):
    o = compile_o(reversed(nodelists[:level])) if level >= 0 else None
    type = nodelist.get("type")
    sort = nodelist.get("sort")
    
    def href(new_offset):
        if node:
            lang = node.lang or request.view_args["lang"]
            return url("node", lang=lang, nodetype=node.type, nid=node.nid(), slug=node.slug(), type=type, sort=sort, o=o, offset=new_offset, _anchor=node.nid())
        else: # responses, problematic:
            return url(request.endpoint, offset=new_offset, **request.view_args)
    
    offset = nodelist["offset"]
    num_total = nodelist["nodes_count"]
    num_per_page = app.config["NUM_NODES_PER_PAGE"]
    
    html = Html()
    if num_total > num_per_page:
        with html.div(class_="pagination"):
            with html.ul():
                num_pages = -(-num_total // num_per_page)
                if offset > 0:
                    new_offset = max(0, offset - num_per_page)
                    with html.li(class_=[]):
                        with html.a(href=href(new_offset), class_=["previous-page", "ajax"]):
                            html.text(Markup("&laquo; ") + _("previous"))
                
                for i in range(num_pages):
                    if offset == num_per_page * i:
                        with html.li(class_="active"):
                            with html.span(class_="current-page"):
                                html.text("%d" % (i+1))
                    else:
                        new_offset = num_per_page * i
                        with html.li(class_=[]):
                            with html.a(href=href(new_offset), class_="ajax"):
                                html.text("%d" % (i+1))
                
                if num_total - offset - num_per_page > 0:
                    new_offset = offset + num_per_page
                    with html.li(class_=[]):
                        with html.a(href=href(new_offset), class_=["next-page", "ajax"]):
                            html.text(_("next") + Markup(" &raquo;"))
    return html
