#autoimport
from flask import Markup
from flaskext.babel import gettext as _
from mysubtree.backend import common
from ..node import Node

class Trash(Node):

    __mapper_args__ = {"polymorphic_identity": "trash"}

    @staticmethod
    def type_name(num):
        return _("trash")

    def __init__(self):
        Node.__init__(self)
        self.type = "trash"
        self.user = common.system_user
        self.username = common.system_username

    @staticmethod
    def always_show_type():
        return True
    
    def title(self):
        return _("trash")
    
    def body_text(self):
        return Markup("<em>%s</em>" % _("Nodes in trash will be permanently deleted after 30 days."))
    
    def slug(self):
        return None
        
    def short_name(self):
        return "_(trash)"
    
    @staticmethod
    def branching():
        return ["items", "comments", "edit-suggestions"] # TODO: generate this list dynamically
    
    def is_posting_forbidden(self):
        return True
    
    def hide_user_and_time(self):
        return True

    @staticmethod
    def is_auxiliary():
        return True
    
    def is_activity_propagation_forbidden(self):
        return True