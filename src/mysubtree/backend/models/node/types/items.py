#autoimport
from flask import Markup
from wtforms import fields, validators
from flask.ext.babel import gettext as _, ngettext
from lib.forms.widgets import TextInput
from lib import utils
from mysubtree.db import db
from comments import Comments

class Items(Comments):
    
    __mapper_args__ = {"polymorphic_identity": "items"}
    
    def __init__(self):
        Comments.__init__(self)
        self.body = ""
    
    @classmethod
    def type_long_name(cls):
        return _("item")
    
    @staticmethod
    def type_name(num):
        return ngettext("%(num)s item", "%(num)s items", num)
    
    @staticmethod
    def str_new_type():
        return _("new item")
    
    @staticmethod
    def str_attach_type():
        return _("Attach item")
    
    @staticmethod
    def get_form_fields(parent_node):
        form = [
            ("name", fields.TextField("", [
                validators.Required(message=_("This field is required.")),
            ])),
        ]
        return form

    def title(self):
        return self.name
    
    def body_text(self):
        return Markup(self.html)
    
    def teaser_length(self):
        return 200
    
    def slug(self):
        return utils.slugify(self.name) 
    
    def short_name(self):
        return utils.short_name(self.name)
    
    @staticmethod
    def is_votable():
        return True
    
    def is_deletable(self):
        return True
    
    def is_renameable(self):
        return True
    
    def is_editable(self):
        return True
    
    def is_allowed_empty_body(self):
        return True
    
    def is_movable(self):
        return True
    
    def is_icon_changeable(self):
        return True
    
    @staticmethod
    def branching():
        return ["items", "comments", "versions", "edit-suggestions", "log-entries", "votes"]
