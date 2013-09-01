from flask.ext.babel import gettext as _
from lib.error import Error
from mysubtree.db import db
from mysubtree.web.user import get_user, get_user_node

_("renamed")

class NodeRenaming:
    def __init__(self):
        pass
    
    def is_renameable(self):
        return False # override in derived classes
    
    def is_renameable_by_current_user(self):
        try:
            self._going_to_rename()
        except Error:
            return False
        return True
    
    def _going_to_rename(self):
        if not self.is_renameable():
            raise Error(_("This node cannot be renamed."))
        if not get_user():
            raise Error(_("You must be logged in to do it."))
        if get_user_node() not in self.get_moderators():
            raise Error(_("You are neither owner nor moderator of that node."))
    
    def rename(self, name):
        self._going_to_rename()
        old_name = self.name
        if self.change("name", name):
            self.log("_(renamed)", from_name=old_name, to_name=self.name)
            return True
        return False
    