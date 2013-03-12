from flask import request
from lib.html import Html
from lib.flaskhelpers.default_url_args import url
from mysubtree.backend import common
from mysubtree.backend.node_ordering import correct_sort_type_of_subnodes, get_sort_types
from mysubtree.web.o import compile_o
from flaskext.babel import gettext as _

def sorting(node, nodelist, nodelists, level):
    o = compile_o(reversed(nodelists[:level])) if level >= 0 else None
    lang = node.lang or request.view_args["lang"]
    type = nodelist["type"]
    sort = correct_sort_type_of_subnodes(nodelist["sort"], node, type)
    
    sort_infos = {
        "newest":   {
            "name":        _("newest"),
            "description": _("newest first"),
        },
        "1day":     {
            "name":        _("top day"),
            "description": _("best voted for the last 24 hours"),
        },
        "1week":    {
            "name":        _("top week"),
            "description": _("best voted for the last 7 days"),
        },
        "1month":   {
            "name":        _("top month"),
            "description": _("best voted for the last 1 month"),
        },
        "1year":    {
            "name":        _("top year"),
            "description": _("best voted for the last 1 year"),
        },
        "alltime":  {
            "name":        _("top all time"),
            "description": _("best voted of all time"),
        },
        "activity": {
            "name":        _("active"),
            "description": _("recently active first"),
        },
    }
    html = Html()
    sort_types = get_sort_types(node, type)
    if len(sort_types) > 1:
        with html.ul(class_="sort"):
            for new_sort in sort_types:
                sort_info = sort_infos[new_sort]
                with html.li():
                    href = url("node", lang=lang, nparent=node.nparent(), nid=node.nid(), slug=node.slug(), type=type, sort=new_sort, o=o, _anchor=node.nid())
                    with html.a(
                        href=href,
                            title=sort_info["description"],
                            class_=[
                                'ajax',
                                "current-sort" if new_sort == sort else ""
                            ]
                    ):
                        html.text(sort_info["name"])
    return html