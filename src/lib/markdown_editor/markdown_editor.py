from flask import Markup
from flask.ext.babel import gettext as _

class MarkdownEditorWidget():
    def __init__(self, preview_position="bottom", top_html="", bottom_html=""):
        self.preview_position = preview_position
        self.top_html = top_html
        self.bottom_html = bottom_html
    def __call__(self, field):
        if field.data is None:
            field.data = ""
        preview = Markup('<span class="mde-preview"></span>')
        if self.preview_position == "bottom":
            top = self.top_html
            bottom = preview + self.bottom_html
        else:
            top = self.top_html + preview
            bottom = self.bottom_html
        return Markup("""
            %(top)s
            <ul class="mde-buttons">
                <li class="strong" title="%(strong)s"></li>
                <li class="emphasis" title="%(emphasis)s"></li>
            </ul>
            <textarea class="mde-textarea" name="%(name)s">%(data)s</textarea>
            %(bottom)s
            """ % {
                "top": top,
                "bottom": bottom,
                "name": field.name,
                "data": field.data,
                "strong": _("Strong"),
                "emphasis": _("Emphasis"),
            }
        )
