# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import desc, or_
from lib import utils
from lib.base57 import base_decode
from mysubtree.db import db
from . import common
from .models.node.node import Node
from .models.node.node_unread import reading_nodes
from mysubtree.web.user import get_user_node
from mysubtree.web.app import app

def get_node(id):
    return Node.query.get(id)

def get_node_from(nid):
    return get_node(base_decode(nid))

def get_node_from_alias(alias):
    return Node.query.filter_by(alias=alias).first()

def get_children(parent):
    return Node.query.filter_by(parent=parent)

#def add_node(node):
    #db.session.add(node)
    #db.session.commit()

#def save_node(node):
    #db.session.commit()


def get_responses_of_current_user(offset):
    user = get_user_node()
    nodes = (Node.query
        .filter_by(parent_user=user)
        .filter(or_(Node.user != user, Node.user == None)) # NULL != "user" is False
        .order_by(desc("created")))
    count = nodes.count() # before _limited
    nodes = _limited(nodes, offset)
    nodes = list(nodes)
    reading_nodes(nodes, user)
    db.session.commit()
    return {"nodes": nodes, "nodes_count": count, "offset": offset}


def get_problematic(user, offset):
    from .models.moderator import Moderator
    nodes = Node.query \
        .filter_by(problematic=True) \
        .join(Moderator.nodes) \
        .filter(Moderator.user == user) \
        .order_by(desc("created"))
    count = nodes.count() # before _limited
    nodes = _limited(nodes, offset)
    return {"nodes": nodes, "nodes_count": count, "offset": offset}


def getting_nodes_below(node):
    node.propagate_rename_if_needed()
    node.propagate_path_rebuild_if_needed()
    db.session.commit()


def get_nodes(parent_node_id, parent_node_type, type, sort, offset):
    if parent_node_type == "users":
        nodes = Node.query.filter_by(user=parent_node_id, type=type)
    else:
        nodes = Node.query.filter_by(parent=parent_node_id, type=type)
    nodes = _sorted(nodes, sort)
    nodes = _limited(nodes, offset)
    nodes = list(nodes)
    reading_nodes(nodes, get_user_node())
    db.session.commit()
    return {"nodes": nodes, "offset": offset, "sort": sort, "type": type}


def _sorted(nodes, sort):
    sort_property = common.sort_properties[sort]
    if sort_property == "created":
        nodes = nodes.order_by(desc("created"))
    else:
        nodes = nodes.order_by(desc(sort_property), desc("created")) # ensure desc(created) is always applied
    return nodes


def _limited(nodes, offset):
    limit = app.config["NUM_NODES_PER_PAGE"]
    nodes = nodes.limit(limit).offset(offset)
    return nodes
