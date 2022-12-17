from datetime import datetime
from flask import request
from flask.ext.babel import gettext as _
from lib.error import Error
from lib.remote_addr import remote_addr
from mysubtree.db import db
from mysubtree.backend.live import live
from mysubtree.backend.models.flag import Flag
from mysubtree.backend.models.user import User
from mysubtree.web.user import get_user_node


def you_already_sent_the_feedback():
    return _("You already sent the feedback.")


def you_already_undid_your_feedback():
    return _("You already undid your feedback.")


class NodeFlagging: # NOTE: tightly coupled with NodeVoting
    
    flags = db.Column(db.Integer())
    problematic = db.Column(db.Boolean())
    num_problematic_here_and_below = db.Column(db.Integer(), default=0)
    
    def __init__(self):
        self.flags = 0
    
    def is_flaggable(self):
        return self.is_votable()
    
    def is_flaggable_by_current_user(self):
        try:
            self._going_to_flag()
        except Error:
            return False
        return True
    
    def is_really_flaggable_by_current_user(self, is_undo=False):
        try:
            self._going_to_flag()
            is_already_flagged_by_user = Flag.query.filter_by(node=self.id, ip=remote_addr()).first() != None
            self._really_going_to_flag(is_already_flagged_by_user, is_undo)
        except Error:
            return False
        return True
    
    def _going_to_flag(self):
        if not self.is_flaggable():
            raise Error(_("This node cannot be flagged."))
        if get_user_node() == self.user:
            raise Error(_("This is created by you. Are you sure it is spam?"))
        if get_user_node() in self.get_moderators():
            raise Error(_("You are moderator of that node."))
    
    def _really_going_to_flag(self, is_already_flagged_by_user, is_undo):
        change = 0
        if not is_undo and not is_already_flagged_by_user:
            change = +1
        if is_undo and is_already_flagged_by_user:
            change = -1
        
        if change == 0:
            if is_undo:
                raise Error(you_already_undid_your_feedback())
            else:
                raise Error(you_already_sent_the_feedback())
        return change
    
    def is_problematic_after_change(self, flags_change=0, votes_change=0):
        return self.flags + flags_change > self.votes_a + votes_change
    
    def flag(self, is_undo):
        self._going_to_flag()
        is_already_flagged_by_user = Flag.query.filter_by(node=self.id, ip=remote_addr()).first() != None
        change = self._really_going_to_flag(is_already_flagged_by_user, is_undo)
        
        if change != 0:
            rowcount = db.session.connection().execute(
                "UPDATE node "
                "SET flags = flags + %(flags_change)s, problematic = %(problematic)s "
                "WHERE id = %(id)s AND type = %(type)s AND flags = %(flags)s",
                {
                    "flags_change": change,
                    "problematic": self.is_problematic_after_change(flags_change=change),
                    "id": self.id,
                    "type": self.type,
                    "flags": self.flags,
                }
            ).rowcount
            live.on_node_update(self.id)
            if rowcount == 0:
                raise Error(_("Temporary error, please try again."))
        
        if change != 0:
            is_making_difference = (
                self.is_problematic_after_change(flags_change=change)
                !=
                self.is_problematic_after_change(flags_change=0)
            )
            if is_making_difference:
                self.propagate_problematic(change)
        
        if change == +1:
            db.session.add(Flag(node=self.id, ip=remote_addr()))
        if change == -1:
            Flag.query.filter_by(node=self.id, ip=remote_addr()).delete()
        
        return change
    
    def is_problematic(self):
        if not self.is_votable():
            return False
        return self.get("problematic")
    
    def propagate_problematic(self, change):
        propagated_moderators = set()
        
        for ancestor in reversed(self.get_full_path() + [self]):
            db.session.connection().execute(
                "UPDATE node "
                "SET num_problematic_here_and_below = num_problematic_here_and_below + %(change)s "
                "WHERE id = %(id)s AND type = %(type)s",
                {
                    "id": ancestor.get("id"),
                    "type": ancestor.get("type"),
                    "change": change,
                }
            )
            moderator = ancestor.get("user")
            if moderator not in propagated_moderators:
                User.query.filter_by(node=moderator).update({User.num_problematic: User.num_problematic + change})
                propagated_moderators.add(moderator)
                live.on_problematic_num_change(moderator)
