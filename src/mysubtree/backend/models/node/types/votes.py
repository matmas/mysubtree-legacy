#autoimport
from flaskext.babel import gettext as _
from mysubtree.db import db
from ..node import Node

class Votes(Node):
    
    __mapper_args__ = {"polymorphic_identity": "votes"}
    
    @staticmethod
    def type_name(num):
        return _("votes")
    
    @classmethod
    def type_long_name(cls):
        return _("vote")
    
    def title(self):
        return "%+d" % self.relative_value
    
    def body_text(self):
        return ""
    
    def slug(self):
        return None
    
    def short_name(self):
        return "%+d" % self.relative_value
    
    @staticmethod
    def branching():
        return []
    
    @staticmethod
    def is_auxiliary():
        return True
    
    def is_activity_propagation_forbidden(self):
        return True