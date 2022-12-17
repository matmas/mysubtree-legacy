from copy import copy
from flask import escape
from flask.ext.babel import gettext as _
from lib.time import utcnow
from lib import utils
from lib.error import Error
from mysubtree.db import db
from mysubtree.backend.models.node.types.all import get_model
from mysubtree.backend.live.live import on_node_update
from mysubtree.web.user import get_user, get_user_node


class NodeEditing:
    
    edited = db.Column(db.DateTime())
    
    def __init__(self):
        pass
    
    def is_editable(self):
        return False  # may be overridden
    
    def is_allowed_empty_body(self):
        return False
    
    def should_edit_without_history(self):
        return False
    
    def is_editable_by_current_user(self):
        try:
            self._going_to_edit()
        except Error:
            return False
        return True
    
    def _going_to_edit(self):
        if not self.is_editable():
            raise Error(_("This node cannot be edited."))
        if self.type == "edit-suggestions":
            raise Error(_("Edit suggestions cannot be edited."))
        if not get_user():
            raise Error(_("You must be logged in to do it."))
        if get_user_node() not in self.get_moderators():
            raise Error(_("You are neither owner nor moderator of that node."))
    
    def is_edit_suggestable_by_current_user(self):
        try:
            self._going_to_suggest_edit()
        except Error:
            return False
        return True
    
    def _going_to_suggest_edit(self):
        if not self.is_editable():
            raise Error(_("This node cannot be edited."))
        if not get_user():
            raise Error(_("You must be logged in to do it."))
        if get_user_node() in self.get_moderators():
            raise Error(_("You cannot edit that node directly."))
    
    def edit(self, new_body, new_version, edit_suggestion=None):
        self._going_to_edit()
        if new_body == "" and not self.is_allowed_empty_body():
            raise Error(_("The text should not be empty."))
        old_body = self.body
        if old_body == new_body:
            return False
        last_version = self._ensure_last_version()
        self._update_body(new_body, new_version)
        
        if not self.should_edit_without_history():
            if edit_suggestion:
                edit_suggestion.change("type", "versions")
                version_node = edit_suggestion
            else:
                version_node = get_model("versions")()
                version_node.body = new_body
                version_node.diff = utils.get_diff(escape(old_body), escape(new_body))
                version_node.version = new_version
                version_node.set_parent(self)
                version_node.add()
                
            # move all child edit-suggestions of self to old version node:id
            from .types.edit_suggestions import EditSuggestions
            for node in EditSuggestions.query.filter_by(parent=self.id):
                node.move_to(last_version)
            
            # move all child edit-suggestions of version_node to parent:
            for node in EditSuggestions.query.filter_by(parent=version_node.id):
                node.move_to(self)
            version_node.log("_(accepted edit)"); _("accepted edit")
        return True

    def _update_body(self, new_body, new_version):
        def update_body(node):
            old_node = copy(node)
            node.body = new_body
            node.edited = utcnow()
            node.ensure_validated()
            
            changes = {}
            for key, value in node.__dict__.iteritems():
                try:
                    if getattr(old_node, key) != value:
                        changes[key] = value
                except AttributeError:
                    if not key.startswith("_"):
                        changes[key] = value
            from .node import Node
            rowcount = Node.query.filter_by(id=node.id, version=new_version - 1).update(dict(changes, version=Node.version + 1))
            on_node_update(node.id)
            if rowcount == 0:
                raise Error(_("Meanwhile the content has changed, so the update was not possible."))
        
        self.change("body", new_body, custom_update_function=update_body)
    
    def _ensure_last_version(self):
        from .types.versions import Versions
        last_version = Versions.query.filter_by(parent=self.id).first()
        if not last_version:
            # create it
            last_version = get_model("versions")()
            last_version.body = self.body
            last_version.diff = self.body
            last_version.set_parent(self)
            last_version.created = self.created
            last_version.version = self.version
            last_version.add()
        return last_version
    
