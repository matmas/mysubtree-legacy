from flask import g
from mysubtree.db import db
from mysubtree.backend.live.live import on_new_response, on_seeing_response
from mysubtree.backend.models.user import User

class NodeUnread:
    
    unread = db.Column(db.Boolean())
    
    def __init__(self):
        pass
    
    def set_unread(self):
        if self.user != self.parent_user:
            self.unread = True
    
    def increment_unread_counter(self, amount):
        # increment unread responses counter of parent node user
        if self.unread and self.user != self.parent_user:
            num_updated = User.query.filter_by(node=self.parent_user).update({User.num_unread_responses: User.num_unread_responses + amount})
            if num_updated > 0:
                on_new_response(self.parent_user)

    def is_just_being_read(self):
        return getattr(self, "_is_just_being_read", False)

def reading_nodes(nodes, user):
    from mysubtree.backend.models.node.node import Node
    unread_nodes = [node for node in nodes if node.unread and node.parent_user == user]
    #unread_nodes = sorted(unread_nodes, key=lambda node: node.type)
    
    unread_nodes_ids = [node.id for node in unread_nodes]
    
    if unread_nodes_ids:
        num_updated = Node.query.filter(Node.id.in_(unread_nodes_ids), Node.unread == True).update({Node.unread: False}, synchronize_session=False)
        if num_updated > 0:
            for node in unread_nodes:
                setattr(node, "_is_just_being_read", True)
            on_seeing_response(node.parent_user)
            User.query.filter_by(node=user).update({User.num_unread_responses: User.num_unread_responses - num_updated})
    