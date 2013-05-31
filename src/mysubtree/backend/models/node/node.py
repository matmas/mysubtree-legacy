from flask import request, url_for
from sqlalchemy import event
from sqlalchemy import DDL
from lib.time import utcnow
from lib.sqlalchemy.datatypes import JSON
from lib.camelcase import decamelcase
from lib.base57 import base_encode
from lib.flaskhelpers.default_url_args import url
from lib.remote_addr import remote_addr
from mysubtree.backend import common
from mysubtree.db import db
from mysubtree.web.app import app
from mysubtree.web.user import get_user_node, get_user_name, get_nick_name
from .node_voting import NodeVoting
from .node_activity import NodeActivity
from .node_hierarchy import NodeHierarchy
from .node_flagging import NodeFlagging
from .node_deleting import NodeDeleting
from .node_renaming import NodeRenaming
from .node_editing import NodeEditing
from .node_moving import NodeMoving
from .node_icon import NodeIcon
from .node_accepting import NodeAccepting
from .node_adding import NodeAdding

def additional_ddl():
    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgresql"):
        ddl = DDL("ALTER SEQUENCE %(table)s_id_seq MINVALUE 10001 START 10001 RESTART 10001;")
    elif app.config["SQLALCHEMY_DATABASE_URI"].startswith("mysql"):
        ddl = DDL("ALTER TABLE %(table)s AUTO_INCREMENT = 10001;")
    event.listen(Node.__table__, "after_create", ddl)
    
    # ensure AUTO_INCREMENT starts at 10001
        #node = Node()
        #node.id = 10000
        #db.session.add(node)
        #db.session.flush()
        #db.session.delete(node)

class Node(db.Model, NodeVoting, NodeActivity, NodeHierarchy, NodeFlagging, NodeDeleting, NodeRenaming, NodeEditing, NodeMoving, NodeIcon, NodeAccepting, NodeAdding):

    id = db.Column(db.Integer(), primary_key=True)
    alias = db.Column(db.String(255)) # for type == "users" pretty urls
    type = db.Column(db.String(255))
    created = db.Column(db.DateTime())
    user = db.Column(db.Integer())
    username = db.Column(db.String(255))
    nickname = db.Column(db.String(255))
    ipaddress = db.Column(db.String(255))
    name = db.Column(db.String(255)) # languages, items, ...
    body = db.Column(db.Text()) # comments, items, versions
    
    version = db.Column(db.Integer()) # comments, items, versions
    diff = db.Column(db.Text()) # versions, edit-suggestions
    
    # Comments, Items:
    html = db.Column(db.Text()) # NOTE: we need to have this definition here and not in subtybe class or else it will be lazy loaded
    teaser = db.Column(db.Text())
    
    # Log entries:
    action = db.Column(db.String(255))
    from_name = db.Column(db.String(255))
    to_name = db.Column(db.String(255))
    from_ = db.Column(JSON())
    to = db.Column(JSON())
    
    # Votes:
    relative_value = db.Column(db.Integer())
    
    __mapper_args__ = {'polymorphic_on': type}
    
    def nid(self):
        return base_encode(self.id)
    
    def nparent(self):
        return base_encode(self.parent)
    
    def url(self, **kwargs):
        kwargs = dict(dict(lang=self.lang or request.view_args["lang"], nodetype=self.type, nid=self.nid(), slug=self.slug()), **kwargs)
        if self.type == "users":
            del kwargs["nid"]
            kwargs["alias"] = self.alias
        # using url unstead of url_for in case we need to pass arguments such as offset and so on, e.g. for making canonical urls
        return url("node", **kwargs)
    
    def url_for(self, endpoint, **kwargs):
        return url_for(endpoint, nid=self.nid(), type=self.type, **kwargs)
    
    def __init__(self):
        NodeVoting.__init__(self)
        NodeActivity.__init__(self)
        NodeHierarchy.__init__(self)
        NodeFlagging.__init__(self)
        NodeDeleting.__init__(self)
        NodeRenaming.__init__(self)
        NodeEditing.__init__(self)
        NodeMoving.__init__(self)
        NodeIcon.__init__(self)
        NodeAccepting.__init__(self)
        NodeAdding.__init__(self)
        
        self.type = decamelcase(self.__class__.__name__, separator="-")
        self.created = utcnow()
        self.user = get_user_node()
        self.username = get_user_name()
        self.nickname = get_nick_name()
        try:
            self.ipaddress = remote_addr()
        except RuntimeError: # working outside of request context
            pass
        self._is_new = True
    
    #---------------------------------------------------------------------------
    @staticmethod
    def type_name(num):
        raise Exception("must be overriden in every class because of gettext")
    
    @classmethod
    def type_long_name(cls):
        return cls.type_name(1) # may be overriden
    
    @staticmethod
    def str_new_type():
        raise Exception("must be overriden in every class, that allows adding by user because of gettext")
    
    @staticmethod
    def always_show_type():
        return False
    
    @staticmethod
    def get_form_default_values(parent_node):
        return () # may be overriden
    
    def hide_user_and_time(self):
        return False #  may be overriden
    
    #---------------------------------------------------------------------------
    
    def ensure_validated(self):
        if not self.get("_validated"):
            self.validate()
    
    def validate(self): # may be extended
        assert not self.get("_validated")
        self._validated = True
    
    #---------------------------------------------------------------------------
    def after_attach(self):
        self.propagate_activity_upwards()
        self.remember_referencing()
    
    #def after_commit(self):
        #print "aa"
    
    #===========================================================================
    
    def log(self, action, user=None, username=None, **kwargs):
        from .types.all import get_model
        entry = get_model("log-entries")(action=action, **kwargs)
        if user:
            entry.user = user
        if username:
            entry.username = username
        entry.set_parent(self)
        entry.add()
    
    #===========================================================================
    
    def get(self, key, default=None):
        return getattr(self, key, default)
    
    def __repr__(self):
        return "%s(name='%s')" % (self.__class__.__name__, self.name)
    
    #===========================================================================
    
    def types_in_menu(self):
        return [type for type in self.branching() if type in ["items", "comments"] and not self.is_posting_forbidden()]

    
additional_ddl()
