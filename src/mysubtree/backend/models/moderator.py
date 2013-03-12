#autoimport
from mysubtree.db import db
from mysubtree.backend.models.node.node import Node

class Moderator(db.Model):
    nodes = db.relationship(Node, backref=db.backref("moderators", cascade="all, delete-orphan"))
    node_id = db.Column(db.Integer(), db.ForeignKey('node.id'), primary_key=True, autoincrement=False)
    user = db.Column(db.Integer(), primary_key=True, autoincrement=False)
    
    def __init__(self, user):
        self.user = user
        
    def __eq__(self, other):
        return self.user == other.user