# -*- coding: utf-8 -*-
from flask import Markup, url_for, g
from flaskext.babel import gettext as _
from lib.html import Html
from .edit.edit import edit
from .accept.accept import accept

def body(node, body_should_expand):
    html = Html()
    is_empty = node.body_text() == ""
    with html.span(
        class_=[
            "body",
            "empty" if is_empty else "",
        ],
        component=True,
    ):
        if node.type in ["items", "trash"] and not is_empty:
            with html.div(class_="clear-body"):
                pass
        if node.get("teaser") and not body_should_expand:
            with html.span(class_="teaser text"):
                html.text(Markup(node.teaser.replace("<!--more-->", u'… <a href="%(href)s" class="more button" title="%(title)s">%(label)s</a>' % {
                    "href": node.url(),
                    "title": _("expand"),
                    "label": "&raquo;",
                })))
            with html.span(class_="full-version text"):
                html.text(node.body_text())
                with html.span(class_=["less", "button"], title=_("collapse")):
                    html.text(Markup("&laquo;"))
        else:
            with html.span(class_="text"):
                html.text(node.body_text())
                if is_empty:
                    if node.is_editable_by_current_user() or node.is_edit_suggestable_by_current_user():
                        html.text(_("(without description)"))
        html.add(edit(node))
        html.add(accept(node))
    return html
