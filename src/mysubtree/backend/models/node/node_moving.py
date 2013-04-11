from flaskext.babel import gettext as _
from lib.error import Error
from mysubtree.web.user import get_user, get_user_node

class NodeMoving:
    def __init__(self):
        pass
    
    def is_movable(self):
        return False # to be overridden
    
    def is_movable_by_current_user(self):
        try:
            self._going_to_move()
        except Error:
            return False
        return True
        
    def _going_to_move(self):
        if not self.is_movable():
            raise Error(_("This node cannot be moved."))
        if not get_user():
            raise Error(_("You must be logged in to do it."))
        if get_user_node() not in self.get_moderators():
            raise Error(_("You are neither owner nor moderator of that node."))
    
    def move(self, destination):
        self._going_to_move()
        if not destination:
            raise Error(_("Could not find the destination node."))
        if self.id == destination.id:
            raise Error(_("Could not move to itself."))
        destination_full_path = destination.get_full_path()
        if any(ancestor["id"] == self.id for ancestor in destination_full_path):
            raise Error(_("Could not move to inside of itself."))
        if self.type not in destination.branching():
            raise Error(_("Could not move %(n1)s to %(n2)s.", n1=self.type, n2=destination.type))
        if destination.type == "trash":
            raise Error(_("Use delete instead."))
        if destination.is_posting_forbidden():
            raise Error(_("Could not move %(n1)s to %(n2)s.", n1=self.type, n2=destination.type))
        
        if self.parent != destination.id:
            
            # check that there will be no cycles:
            if self.id in [ancestor["id"] for ancestor in destination_full_path]:
                raise Error(_("Could not move to inside of itself."))
            # NOTE: there is a chance of cycle occuring when destination.path is out of sync (when propagation did not catched up yet)
            #       detect them at propagation-time and resolve them by moving to root/trash
            
            source_node = self.get_parent()
            self.move_to(destination)
            self.log("_(moved)", from_=source_node, to=destination); _("moved")
            self.on_moving()
            return True
        return False