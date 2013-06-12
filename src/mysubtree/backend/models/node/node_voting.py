from datetime import timedelta
from flask import request
from flaskext.babel import gettext as _
from sqlalchemy import desc
from lib.time import utcnow
from lib.error import Error
from lib.remote_addr import remote_addr
from mysubtree.backend import common
from mysubtree.backend.models.node.types.all import get_model, get_all_types
from mysubtree.backend.models.decrement import Decrement
from mysubtree.backend.live.live import on_node_update
from mysubtree.db import db
from mysubtree.web.user import get_user, get_user_node

def you_like_it_already():
    return _("You like it already.")

def no_like_to_undo():
    return _("No like to undo.")

def additional_fields():
    for type in get_all_types():
        setattr(NodeVoting, "votes_sum_%s_d" % type, db.Column(db.Integer(), default=0))
        setattr(NodeVoting, "votes_sum_%s_w" % type, db.Column(db.Integer(), default=0))
        setattr(NodeVoting, "votes_sum_%s_m" % type, db.Column(db.Integer(), default=0))
        setattr(NodeVoting, "votes_sum_%s_y" % type, db.Column(db.Integer(), default=0))
        setattr(NodeVoting, "votes_sum_%s_a" % type, db.Column(db.Integer(), default=0))

class NodeVoting:
    
    votes_d = db.Column(db.Integer(), default=0)
    votes_w = db.Column(db.Integer(), default=0)
    votes_m = db.Column(db.Integer(), default=0)
    votes_y = db.Column(db.Integer(), default=0)
    votes_a = db.Column(db.Integer(), default=0)
    
    def __init__(self):
        if self.is_votable():
            self.votes_d = 0
            self.votes_w = 0
            self.votes_m = 0
            self.votes_y = 0
            self.votes_a = 0
    
    def is_votable(self):
        return False
    
    def is_votable_by_current_user(self):
        try:
            self._going_to_vote()
        except Error:
            return False
        return True
    
    def is_likable_by_current_user(self, is_undo=False):
        try:
            self._going_to_vote()
            last_vote_node = self._get_last_vote_node(remote_addr())
            self._going_to_like(last_vote_node, is_undo=is_undo)
        except Error:
            return False
        return True
    
    def _going_to_vote(self):
        #if not get_user():
            #raise Error(_("You must be logged in to do it."))
        if not self.is_votable():
            raise Error(_("This node cannot be voted for."))
        if self.get("ipaddress") == remote_addr():
            raise Error(_("This node is created by your IP address. The author is not allowed to vote for his node. Wait for the likes from others."))
        if get_user_node() == self.user:
            raise Error(_("This node is created by you. The author is not allowed to vote for his node. Wait for the likes from others."))
    
    def _going_to_like(self, last_vote_node, is_undo):
        if not last_vote_node:
            if not is_undo:
                relative_value = +1
            else:
                raise Error(no_like_to_undo())
        elif last_vote_node.user != get_user_node() and last_vote_node.relative_value == +1:
            if is_undo:
                if not last_vote_node.user and last_vote_node.ipaddress:
                    raise Error(_("From your IP address has been voted +1 for it while being logged off. Log off and try again."))
                else:
                    raise Error(_("From your IP address has been voted +1 for it by another user. Undo is not possible."))
            else:
                raise Error(_("From your IP address has been voted +1 for it."))
        else:
            if last_vote_node.relative_value == +1:
                if not is_undo:
                    raise Error(you_like_it_already())
                else:
                    relative_value = -1
            else:
                assert last_vote_node.relative_value == -1
                if not is_undo:
                    relative_value = +1
                else:
                    raise Error(no_like_to_undo())
        return relative_value
    
    def get_votes(self, sort):
        return getattr(self, common.display_votes_on_sort[sort])
    
    def vote(self, is_undo):
        self._going_to_vote()
        last_vote_node = self._get_last_vote_node(remote_addr())
        relative_value = self._going_to_like(last_vote_node, is_undo=is_undo)
        
        now = utcnow()
        
        if relative_value < 0 and last_vote_node and last_vote_node.created + timedelta(minutes=30) > now:
            now = last_vote_node.created
            is_votenode_created = False
            last_vote_node.remove()
        else:
            newnode = get_model("votes")()
            newnode.set_parent(self)
            newnode.relative_value = relative_value
            newnode.adding = utcnow()
            newnode.add()
            is_votenode_created = True
        
        this_hour   = now.replace(microsecond=0, second=0, minute=0)
        this_day    = this_hour.replace(hour=0)
        this_month  = this_day.replace(day=1)
        now_plus_1d = this_hour  + timedelta(days=1)
        now_plus_1w = this_day   + timedelta(days=7)
        now_plus_1m = this_day   + timedelta(days=30)
        now_plus_1y = this_month + timedelta(days=365)
        
        #-----------------------------------------------------------------------
        rowcount = db.session.connection().execute("UPDATE node "
            "SET votes_a = votes_a + %(relative_value)s, "
            "problematic = %(problematic)s "
            "WHERE id = %(id)s AND type = %(type)s AND votes_a = %(votes_a)s",
            {
                "id": self.id,
                "type": self.type,
                "relative_value": relative_value,
                "problematic": self.is_problematic_after_change(votes_change=relative_value),
                "votes_a": self.votes_a,
            }
        ).rowcount
        if rowcount == 0:
            raise Error(_("Temporary error, please try again."))
        
        is_making_difference = (
            self.is_problematic_after_change(votes_change=relative_value)
            !=
            self.is_problematic_after_change(votes_change=0)
        )
        if is_making_difference:
            self.propagate_problematic(-relative_value) # negative because votes are the opposite of the flags
        #-----------------------------------------------------------------------
        
        on_node_update(self.id)
        
        db.session.connection().execute("UPDATE node "
            "SET votes_sum_"+self.type+"_a = votes_sum_"+self.type+"_a + %(relative_value)s "
            "WHERE id = %(id)s AND type = %(type)s",
        {"id": self.parent, "type": self.parent_type, "relative_value": relative_value})
        on_node_update(self.parent)
        
        for counter, how in {
            "votes_d":              {"at": now_plus_1d, "node": self.id, "type": self.type},
            "votes_w":              {"at": now_plus_1w, "node": self.id, "type": self.type},
            "votes_m":              {"at": now_plus_1m, "node": self.id, "type": self.type},
            "votes_y":              {"at": now_plus_1y, "node": self.id, "type": self.type},
            "votes_sum_%(type)s_d": {"at": now_plus_1d, "node": self.parent, "type": self.parent_type},
            "votes_sum_%(type)s_w": {"at": now_plus_1w, "node": self.parent, "type": self.parent_type},
            "votes_sum_%(type)s_m": {"at": now_plus_1m, "node": self.parent, "type": self.parent_type},
            "votes_sum_%(type)s_y": {"at": now_plus_1y, "node": self.parent, "type": self.parent_type},
        }.iteritems():
            counter = counter % {"type": self.type}
            params = {
                "node": how["node"],
                "type": how["type"],
                "at": how["at"],
                "counter": counter,
                "relative_value": relative_value,
            }
            db.session.connection().execute(
                "UPDATE node SET \""+counter+"\" = \""+counter+"\" + %(relative_value)s WHERE id = %(node)s AND type = %(type)s", params
            )
            rowcount = db.session.connection().execute(
                "UPDATE decrement SET amount = amount + %(relative_value)s WHERE node = %(node)s AND type = %(type)s AND at = %(at)s AND counter = %(counter)s", params
            ).rowcount
            if rowcount == 0:
                db.session.connection().execute(
                    "INSERT INTO decrement (node, type, at, amount, counter) VALUES (%(node)s, %(type)s, %(at)s, %(relative_value)s, %(counter)s)", params
                )
        
        return relative_value, is_votenode_created

    def _get_last_vote_node(self, ipaddress):
        from .types.votes import Votes
        return Votes.query.filter_by(parent=self.id, ipaddress=ipaddress).order_by(desc("created")).first()

additional_fields()
