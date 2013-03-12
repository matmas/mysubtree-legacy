#autoimport
from flaskext.babel import gettext as _
from lib import utils
from mysubtree.backend import common
from mysubtree.db import db
from mysubtree.web.babel import get_browser_locale
from ..node import Node
from .root import Root

class Users(Node):
    
    __mapper_args__ = {"polymorphic_identity": "users"}
    
    @staticmethod
    def type_name(num):
        return _("users")
    
    def __init__(self, data=None, username=None):
        Node.__init__(self, data)
        if not data:
            self.parent = common.users_parent
            self.username = username
            self.set_parent(None)
            #self.lang = get_browser_locale()
    
    def after_attach(self):
        Node.after_attach(self)
        self.user = self.id
    
    def is_posting_forbidden(self):
        return True
    
    @classmethod
    def type_long_name(cls):
        return _("user")
    
    @staticmethod
    def always_show_type():
        return True
    
    def title(self):
        if self.username:
            return self.username
        else:
            return self.nid()
        
    def body_text(self):
        return ""
        
    def slug(self):
        return utils.slugify(self.username) 

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
    
    @staticmethod
    def should_not_consider_auxiliary():
        return True
    
    def is_activity_propagation_forbidden(self):
        return True
