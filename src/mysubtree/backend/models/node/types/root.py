#autoimport
from flask.ext.babel import gettext as _
from lib.base57 import base_decode
from mysubtree.backend import common
from mysubtree.db import db
from ..node import Node


class Root(Node):

    __mapper_args__ = {"polymorphic_identity": "root"}

    @staticmethod
    def type_name(num):
        return _("root")

    def __init__(self):
        Node.__init__(self)
        self.type = "root"
        self.user = common.system_user
        self.username = common.system_username
    
    def title(self):
        return _("root")
    
    def body_text(self):
        return ""
    
    def slug(self):
        return None
        
    def short_name(self):
        return "_(root)"
    
    @staticmethod
    def branching():
        return ["items", "trash"]

    def hide_user_and_time(self):
        return True
    
    def is_activity_propagation_forbidden(self):
        return True
