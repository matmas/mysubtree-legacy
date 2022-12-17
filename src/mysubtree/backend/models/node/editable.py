#autoimport
from flask import Markup
from flask.ext.babel import gettext as _
from wtforms import fields, validators
from tidylib import tidy_document
#from lib.forms.widgets import TextArea
from lib.forms import widgets
from lib import utils
from lib.markdown import markdown
from .node import Node


class Editable(Node):
    
    @staticmethod
    def get_form_fields(parent_node):
        return [
            ("body", fields.TextAreaField("", [
                validators.Required(message=_("This field is required.")),
            #], widget=widgets.WikiareaWidget())),
            ])),
        ]
    
    def teaser_length(self):
        return 1024
    
    def validate(self):
        super(Editable, self).validate()
        
        self.html = markdown.to_html(self.body)
        
        if not self.version:
            self.version = 1
        
        if len(self.html) > self.teaser_length():
            teaser = utils.short_name(self.html, max_length=self.teaser_length(), append_ellipsis=False)
            if teaser.endswith("<"):
                teaser = teaser.rstrip("<")
            teaser += '<!--more-->'
            teaser, errors = tidy_document(teaser, options={'numeric-entities': 1, "show-body-only": 1})
            self.teaser = teaser
    
    def body_text(self):
        return Markup(self.html)
    
    def is_editable(self):
        return True
    