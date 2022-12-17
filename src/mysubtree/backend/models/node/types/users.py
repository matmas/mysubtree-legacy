#autoimport
from flask import Markup
from flask.ext.babel import gettext as _
from lib import utils
from mysubtree.backend import common
from mysubtree.db import db
from mysubtree.web.babel import get_browser_locale
from ..editable import Editable
from .root import Root
from .responses import Responses


class Users(Editable):
    
    __mapper_args__ = {"polymorphic_identity": "users"}
    
    @staticmethod
    def type_name(num):
        return _("users")
    
    def __init__(self, username=None, alias=None):
        Editable.__init__(self)
        self.parent = common.users_parent
        self.username = username
        self.alias = alias
        self.set_parent(None)
    
    def after_attach(self):
        Editable.after_attach(self)
        db.session.flush() # for getting the self.id
        self.user = self.id # remember the generated user id
        db.session.add(Responses(self.user)) # create responses node for this user
    
    def is_posting_forbidden(self):
        return True
    
    @classmethod
    def type_long_name(cls):
        return _("user")
    
    @staticmethod
    def always_show_type():
        return True
    
    def title(self):
        return "%s (%s)" % (self.alias, self.username)
        
    def slug(self):
        return None

    def short_name(self):
        if self.username:
            return utils.short_name(self.username)
        else:
            return self.nid()
    
    @staticmethod
    def branching():
        return ["items", "comments", "versions", "edit-suggestions", "log-entries", "votes"]
    
    def hide_user_and_time(self):
        return True
    
    def is_allowed_empty_body(self):
        return True
    
    def should_edit_without_history(self):
        return True
    
    @staticmethod
    def should_not_consider_auxiliary():
        return True
    
    def is_activity_propagation_forbidden(self):
        return True
