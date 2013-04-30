#autoimport
from flask import Markup, escape, g
from flask_wtf import fields, validators
from flaskext.babel import gettext as _, ngettext
from lib import utils
from lib.wtforms import widgets
from lib.error import Error
from lib.markdown import markdown
from ..node import Node
from mysubtree.backend import backend

class EditSuggestions(Node):

    __mapper_args__ = {"polymorphic_identity": "edit-suggestions"}

    @staticmethod
    def type_name(num):
        return ngettext("%(num)s edit suggestion", "%(num)s edit suggestions", num)

    @staticmethod
    def str_new_type():
        return _("change text")
    
    @staticmethod
    def str_attach_type():
        return _("suggest edit")
    
    #@staticmethod
    #def get_form_fields(parent_node):
        #return [
            #("body", fields.TextAreaField("", [
                #validators.Required(message=_("This field is required.")),
            #], widget=widgets.WikiareaWidget(
                #preview_position="top" if g.is_ajax else "bottom",
                #top_html=Markup("<div class='clear-body'></div>") if parent_node.type == "items" else "",
            #))),
            #("version", fields.HiddenField()),
        #]
    
    @classmethod
    def type_long_name(cls):
        return _("edit suggestion")
    
    def title(self):
        return ""
        
    def body_text(self):
        return Markup('<span class="diff">%s</span>' % self.diff)
    
    def slug(self):
        return None
    
    def short_name(self):
        return utils.short_name(self.body)
    
    @staticmethod
    def is_votable():
        return True
    
    def is_deletable(self):
        return True
    
    def is_editable(self):
        return True
    
    @staticmethod
    def branching():
        return ["comments", "edit-suggestions", "log-entries", "votes"]
    
    def validate(self):
        super(EditSuggestions, self).validate()
        if self.get("_is_new"):
            if self.body == self.get_parent().body:
                raise Error(_("No changes?"))
            
            self.version = int(self.version)
            if self.version - 1 != self.get_parent().version:
                raise Error(_("Meanwhile, a different edit suggestion has been accepted. Warning: your changes were not saved."))
            elif self.parent_type == "versions": # posting edit-suggestion too late as well because, parent one is already accepted as a version
                comment_node = backend.get_node(self.parent_of_parent)
                if self.version - 1 != comment_node.version:
                    raise Error(_("Meanwhile, a different edit suggestion has been accepted. Warning: your changes were not saved."))
                self.set_parent(comment_node) # we should move it directly below comment node
            self.diff = utils.get_diff(escape(self.get_parent().body), escape(self.body))
    
    ###=========================================================================
    def is_acceptable(self):
        return True
    
    def accept(self):
        super(Node, self).accept()
        return self.get_parent().edit(self.body, self.version, self)
    ###=========================================================================