from flask.ext.babel import gettext as _
from lib.error import Error
from lib.time import utcnow
from mysubtree.web.user import get_user, get_user_node
from mysubtree.db import db, get_trash_id


class NodeDeleting:
    
    previous_location = db.Column(db.Integer())
    deleted_when = db.Column(db.DateTime())
    
    def __init__(self):
        pass
    
    def is_deletable(self):
        return False # for derived types to override
    
    def is_deletable_by_current_user(self):
        try:
            self._going_to_delete()
        except Error:
            return False
        return True
        
    def is_restorable_by_current_user(self):
        try:
            self._going_to_restore()
        except Error:
            return False
        return True
    
    def _going_to_delete(self):
        if not self.is_deletable():
            raise Error(_("This node cannot be deleted."))
        if not get_user():
            raise Error(_("You must be logged in to do it."))
        if get_user_node() not in self.get_moderators():
            raise Error(_("You are neither owner nor moderator of that node."))
        if self.is_deleted():
            raise Error(_("It is already deleted."))
    
    def _going_to_restore(self):
        if not self.is_deletable():
            raise Error(_("This node cannot be restored."))
        if not get_user():
            raise Error(_("You must be logged in to do it."))
        if get_user_node() not in self.get_moderators():
            raise Error(_("You are neither owner nor moderator of that node."))
        if not self.is_deleted():
            raise Error(_("It is not deleted."))
    
    def delete(self):
        self._going_to_delete()
        from mysubtree.backend import backend
        trash = backend.get_node(get_trash_id(self.lang))
        self.previous_location = self.parent # remember last location
        self.move_to(trash)
        self.log("_(deleted)"); _("deleted")
        self.deleted_when = utcnow()
    
    def restore(self): # restore from trash to previous location
        self._going_to_restore()
        from mysubtree.backend import backend
        previous_location = backend.get_node(self.previous_location)
        self.move_to(previous_location)
        self.log("_(restored)"); _("restored")
        self.deleted_when = None
    
    def is_deleted(self):
        return self.parent_type == "trash"
    
    def on_moving(self):
        self.deleted_when = None
