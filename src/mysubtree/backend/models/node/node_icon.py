from flaskext.babel import gettext as _
from lib.error import Error
from mysubtree.web.user import get_user, get_user_node
from mysubtree.db import db

class NodeIcon:
    
    icon = db.Column(db.String(65536))
    
    def __init__(self):
        pass
    
    def is_icon_changeable(self):
        return False # to be overridden
    
    def is_icon_changeable_by_current_user(self):
        try:
            self._going_to_set_icon()
        except Error:
            return False
        return True
    
    def _going_to_set_icon(self):
        if not self.is_icon_changeable():
            raise Error(_("Icon of this node cannot be changed."))
        if not get_user():
            raise Error(_("You must be logged in to do it."))
        if get_user_node() not in self.get_moderators():
            raise Error(_("You are neither owner nor moderator of that node."))
    
    def set_icon(self, icon):
        self._going_to_set_icon()
        if self.change("icon", icon):
            self.log("_(changed icon)"); _("changed icon")
            return True
        return False