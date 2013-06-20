from flaskext.babel import format_date, gettext as _
from lib.html import Html
from mysubtree.backend.models.node.types.all import get_model
from mysubtree.web.templatefilters import timesince as timesince_filter, activity_level

def timesince(node):
    html = Html()
    with html.span(
        class_=[
            "timesince",
            activity_level(node.created),
            "edits-%s" % activity_level(node.created) if node.type == "edit-suggestions" else "",
        ],
        title="%(created)s %(exactly)s" % {
            "created": _("created"),
            "exactly": format_date(node.created)},
    ):
        html.text(timesince_filter(node.created))
        html.text(" ")
    return html