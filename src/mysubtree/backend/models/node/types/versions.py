#autoimport
from flask import Markup
from flask_wtf import fields, validators
from flask.ext.babel import gettext as _, ngettext
from lib.forms import widgets
from lib import utils
from lib.markdown import markdown
from mysubtree.db import db
from mysubtree.backend.models.node.types.all import get_model
from ..node import Node


class Versions(Node):
    
    __mapper_args__ = {"polymorphic_identity": "versions"}
    
    @classmethod
    def type_long_name(cls):
        return _("version")
    
    @staticmethod
    def type_name(num):
        return ngettext("%(num)s version", "%(num)s versions", num)
    
    def title(self):
        return "1. %s" % _("(original)") if self.version == 1 else "%d." % self.version
    
    def body_text(self):
        return Markup('<span class="diff">%s</span>' % self.diff)
    
    def slug(self):
        return None
    
    def short_name(self):
        return utils.short_name(self.body)
    
    @staticmethod
    def branching():
        return get_model("edit-suggestions").branching()
    
    @staticmethod
    def is_auxiliary():
        return True
