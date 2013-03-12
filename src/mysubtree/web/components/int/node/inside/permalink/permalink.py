from flaskext.babel import format_datetime, gettext as _
from lib.html import Html

def permalink(node):
    html = Html()
    with html.a(
        href=node.url(),
        class_="permalink",
        title=_("permalink"),
        component=True,
    ):
        pass
    return html
