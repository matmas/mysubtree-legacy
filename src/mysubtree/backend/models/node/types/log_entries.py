#autoimport
# -*- coding: utf-8 -*-
from ..node import Node
from flask import Markup, url_for, g
from flaskext.babel import gettext as _
from lib.base57 import base_encode
from mysubtree.db import db
from mysubtree.web.templatefilters import content_gettext as __

class LogEntries(Node):

    __mapper_args__ = {"polymorphic_identity": "log-entries"}
    
    @staticmethod
    def type_name(num):
        return _("log")

    @classmethod
    def type_long_name(cls):
        return _("log entry")
    
    def __init__(self, action=None, from_=None, to=None, from_name=None, to_name=None):
        Node.__init__(self)
        self.action = action
        if from_:
            self.from_ = {
                "lang": from_.lang,
                "type": from_.type,
                "parent": from_.parent,
                "id": from_.id,
                "slug": from_.slug(),
                "short_name": from_.short_name(),
            }
        if to:
            self.to = {
                "lang": to.lang,
                "type": to.type,
                "parent": to.parent,
                "id": to.id,
                "slug": to.slug(),
                "short_name": to.short_name(),
            }
        if from_name:
            self.from_name = from_name
        if to_name:
            self.to_name = to_name
    
    def title(self):
        return __(self.action)
    
    def body_text(self):
        if self.from_name and self.to_name:
            return Markup(u"%s <b>→</b> %s" % (self.from_name, self.to_name))
        if self.from_ and self.to:
            return Markup(u'<a href="%s">%s</a> <b>→</b> <a href="%s">%s</a>' % (
            url_for("node", lang=self.from_["lang"], nodetype=self.from_["type"], nid=base_encode(self.from_["id"]), slug=self.from_["slug"]),
            __(self.from_["short_name"]),
            url_for("node", lang=self.to["lang"], nodetype=self.to["type"], nid=base_encode(self.to["id"]), slug=self.to["slug"]),
            __(self.to["short_name"]),
        ))
        return ""
    
    def slug(self):
        return None
        
    def short_name(self):
        return self.action
    
    @staticmethod
    def branching():
        return ["comments"]
        
    @staticmethod
    def is_auxiliary():
        return True