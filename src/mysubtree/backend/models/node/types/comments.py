#autoimport
from flask import Markup
from flask_wtf import fields, validators
from flask.ext.babel import gettext as _, ngettext
from tidylib import tidy_document
from lib.forms.widgets import TextArea
from lib.forms import widgets
from lib import utils
from lib.markdown import markdown
from mysubtree.db import db
from ..editable import Editable

class Comments(Editable):
    
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
    
    def title(self):
        return ""
    
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
    
    @staticmethod
    def branching():
        return ["comments", "edit-suggestions", "versions", "log-entries", "votes"]
    