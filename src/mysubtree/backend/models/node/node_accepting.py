from flaskext.babel import gettext as _
from lib.error import Error
from mysubtree.web.user import get_user, get_user_node

class NodeAccepting:
    def __init__(self):
        pass
    
    def is_acceptable(self):
        return False # to be overridden

    def is_acceptable_by_current_user(self):
        try:
            self._going_to_accept()
        except Error:
            return False
        return True

    def _going_to_accept(self):
        if self.type == "versions":
            raise Error(_("This edit suggestion is already accepted."))
        if not self.is_acceptable():
            raise Error(_("This node is not acceptable."))
        if self.parent_type == "edit-suggestions":
            raise Error(_("This edit suggestion is not yet possible to accept."))
        if self.parent_type == "versions":
            raise Error(_("This edit suggestion is not possible to accept anymore because a different one was accepted."))
        if not get_user():
            raise Error(_("You must be logged in to do it."))
        if get_user_node() not in self.get_moderators(with_user=False): # quicker than self.get_parent().get_moderators()
            raise Error(_("Only moderator can accept that."))
    
    def accept(self):
        self._going_to_accept() # to be extended in subclasses
    