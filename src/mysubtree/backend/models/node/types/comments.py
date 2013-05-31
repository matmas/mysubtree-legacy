#autoimport
from flask import Markup
from flask_wtf import fields, validators
from flaskext.babel import gettext as _, ngettext
from tidylib import tidy_document
from lib.wtforms.widgets import TextArea
from lib.wtforms import widgets
from lib import utils
from lib.markdown import markdown
from mysubtree.db import db
from ..node import Node

class Comments(Node):
    
    __mapper_args__ = {"polymorphic_identity": "comments"}
    
    @classmethod
    def type_long_name(cls):
        return _("comment")
    
    @staticmethod
    def type_name(num):
        return ngettext("%(num)s comment", "%(num)s comments", num)
    
    @staticmethod
    def str_new_type():
        return _("new comment")
    
    @staticmethod
    def str_attach_type():
        return _("Attach comment")
    
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
        super(Comments, self).validate()
        
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
    
    def title(self):
        return ""
    
    def body_text(self):
        return Markup(self.html)
    
    def slug(self):
        return None
    
    def short_name(self):
        return utils.short_name(self.body)
    
    @staticmethod
    def is_votable():
        return True
    
    def is_deletable(self):
        return True
    
    def is_movable(self):
        return True
    
    def is_editable(self):
        return True
    
    @staticmethod
    def branching():
        return ["comments", "edit-suggestions", "versions", "log-entries", "votes"]
    