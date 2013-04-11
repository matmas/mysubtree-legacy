from flaskext.babel import gettext as _
from lib.sqlalchemy.datatypes import JSON
from mysubtree.backend import common
from mysubtree.backend.live.live import on_node_move, on_node_update
from mysubtree.db import db, get_trash_id
from .types.all import get_all_types
from .node_unread import NodeUnread

def additional_fields():
    possible_branching_types = get_all_types()
    for type in possible_branching_types:
        setattr(NodeHierarchy, "count_of_%s" % type, db.Column(db.Integer(), default=0))

class NodeHierarchy(NodeUnread):
    
    parent = db.Column(db.Integer())            # NOTE: after node move, self must update
    parent_type = db.Column(db.String(255))     # NOTE: after node move, self must update
    parent_user = db.Column(db.Integer())       # NOTE: after node move, self must update
    parent_of_parent = db.Column(db.Integer())  # NOTE: after node move, self + children must update
    path = db.Column(JSON())                    # NOTE: after node move, all descendants must update
    lang = db.Column(db.String(255))            # NOTE: after node move, all descendants must update
    count_of_active_grandchildren = db.Column(db.Integer(), default=0)
    propagate_slug_and_short_name_rebuild = db.Column(db.Boolean())
    propagate_path_rebuild = db.Column(db.Boolean())
    references = db.Column(JSON())
    
    def __init__(self):
        NodeUnread.__init__(self)
        self.parent = None
        self.parent_type = None
        self.parent_of_parent = None
        self.path = []
        self.lang = None
        self.references = []
        
        self._parent_node = None # just for caching parent node for some operations
    
    #===========================================================================
    
    def get_moderators(self, with_user=True):
        return list(set(
            [ancestor["user"] for ancestor in self.path] + ([self.user] if with_user else [])
            # [ancestor["user"] for ancestor in self.path if ancestor["user"]] + ([self.user] if self.user and with_user else [])
        ))
    
    #===========================================================================
    
    def is_posting_forbidden(self):
        return False
    
    @staticmethod
    def is_auxiliary():
        return False
    
    @staticmethod
    def should_not_consider_auxiliary():
        return False
    
    #===========================================================================
    
    def remember_referencing(self):
        from .node import Node
        
        for property in ["from_", "to"]:
            reference = getattr(self, property, None)
            if reference:
                node = Node.query.get(reference["id"])
                
                if not self.id:
                    db.session.add(self)
                    db.session.flush()
                
                node.references = node.references + [{
                    "property": property,
                    "id": self.id,
                }]
    
    #===========================================================================
    
    @classmethod
    def _count(cls, type):
        return getattr(cls, "count_of_%s" % type)
    
    def count(self, type):
        return getattr(self, "count_of_%s" % type)

    def increment_counters(self, amount=1, parent_counter=True, user_counter=True, parent_user_counter=True):
        from .node import Node
        
        # increment parent counter
        if parent_counter and self.parent:
            db.session.connection().execute(
                "UPDATE node "
                "SET \"count_of_%(type)s\" = \"count_of_%(type)s\" + %(amount)s "
                "WHERE id = '%(id)s'" % {
                    "type": self.type,
                    "amount": amount,
                    "id": self.parent,
                })
            on_node_update(self.parent)
            
        # increment user counter
        if user_counter and self.user:
            db.session.connection().execute(
                "UPDATE node "
                "SET \"count_of_%(type)s\" = \"count_of_%(type)s\" + %(amount)s "
                "WHERE id = '%(id)s'" % {
                    "type": self.type,
                    "amount": amount,
                    "id": self.user,
                })
            on_node_update(self.user)
        
        self.increment_unread_counter(amount)
        
        # increment parent of parent counter (for reducing the number of sorting tabs)
        if self.parent_of_parent and not self.is_activity_propagation_forbidden():
            db.session.connection().execute(
                "UPDATE node "
                "SET count_of_active_grandchildren = count_of_active_grandchildren + %(amount)s "
                "WHERE id = '%(id)s'" % {
                    "amount": amount,
                    "id": self.parent_of_parent,
                })
            on_node_update(self.parent_of_parent)
    
    #===========================================================================
    
    def set_parent(self, node):
        self._parent_node = node
        if node:
            self.parent = node.id
            self.parent_type = node.type
            self.parent_of_parent = node.parent
            self.parent_user = node.user
            self.path = node._path_for_subnodes()
            self.lang = node.lang # inherit from parent
            self.set_moderators(node._moderators_for_subnodes(self.user))
            self.set_unread()

    def get_parent(self):
        from mysubtree.backend.backend import get_node
        if not self.get("_parent_node"):
            self._parent_node = get_node(self.parent)
        return self._parent_node
    
    #===========================================================================
    
    def set_moderators(self, moderators):
        if not self.moderators:
            self.moderators = moderators
        else:
            to_insert = set(moderators) - set(self.moderators) 
            to_delete = set(self.moderators) - set(moderators)
            for moderator in to_delete:
                self.moderators.remove(moderator)
            for moderator in to_insert:
                self.moderators.append(moderator)
    
    def _moderators_for_subnodes(self, subnode_user):
        from mysubtree.backend.models.moderator import Moderator
        moderators = self.get_moderators()
        if self.user not in moderators:
            moderators = [self.user] + moderators
        if subnode_user not in moderators:
            moderators = [subnode_user] + moderators
        return [Moderator(user) for user in moderators if user]
        
    
    def _path_for_subnodes(self):
        path = self.path + [self._path_segment()]
        
        # cut long path:
        max_path_length = 10
        if len(path) > max_path_length:
            num_to_skip = len(path) - max_path_length
            path = path[num_to_skip:]
            assert len(path) == max_path_length
        
        return path
    
    def has_full_path(self):
        if self.path and self.path[0]["type"] != "root" and self.path[0]["type"] != "users": # NOTE: all top-level types should be here
            return False
        else:
            return True
    
    def get_full_path(self):
        from mysubtree.backend.backend import get_node
        full_path = self.path
        if not self.has_full_path():
            node = self
            while not node.has_full_path():
                node = get_node(node.path[0]["id"])
                full_path[0:0] = node.path
        return full_path
    
    def _path_segment(self):
        return {
            "id": self.id,
            "parent": self.parent,
            "slug": self.slug(),
            "short_name": self.short_name(),
            "type": self.type,
            "user": self.user,
        }
    
    #===========================================================================
    
    def move_to(self, destination_node):
        self.propagate_problematic(-self.num_problematic_here_and_below)
        self.increment_counters(amount=-1, user_counter=False)
        self.set_parent(destination_node)
        self.increment_counters(amount=+1, user_counter=False)
        self.propagate_problematic(+self.num_problematic_here_and_below)
        self.invalidate_path()
        on_node_move(self)
    
    def change(self, field, new_value, custom_update_function=None):
        if self.get(field) != new_value:
            old_short_name = self.short_name()
            old_slug = self.slug()
            
            if field == "type":
                self.increment_counters(amount=-1)
            
            if custom_update_function:
                custom_update_function(self)
            else:
                setattr(self, field, new_value) # also update local copy
                db.session.flush() # save
                on_node_update(self.id)
            
            if field == "type":
                self.increment_counters(amount=+1)
            
            if field in self._path_segment():
                self.invalidate_path()
            elif old_short_name != self.short_name() or old_slug != self.slug():
                self.invalidate_short_name_and_slug_in_path() # sufficient, more efficient AND takes care of references
            return True
        return False
    
    def remove(self):
        self.increment_counters(amount=-1)
        db.session.delete(self)
    
    #===========================================================================
    
    def invalidate_path(self):
        from .node import Node
        from mysubtree.backend.models.moderator import Moderator
        Node.query.filter_by(parent=self.id).update({
            "parent_of_parent": self.parent,
            "path": self._path_for_subnodes(),
            "propagate_path_rebuild": True,
        })
        for node in Node.query.filter_by(parent=self.id):
            node.set_moderators(self._moderators_for_subnodes(node.user))
    
    
    def propagate_path_rebuild_if_needed(self):
        from mysubtree.backend.models.moderator import Moderator
        if self.propagate_path_rebuild:
            # Cycle detector:
            if self.id in [ancestor["id"] for ancestor in self.path]:
                from mysubtree.backend import backend
                trash = backend.get_node(get_trash_id(self.lang))
                self.previous_location = self.parent # remember last location
                self.move_to(trash)
                self.log("_(deleted)", user=common.system_user, username=common.system_username); _("deleted")
                
            from .node import Node
            Node.query.filter_by(parent=self.id).update({"propagate_path_rebuild": True, "path": self._path_for_subnodes(), "lang": self.lang})
            for node in Node.query.filter_by(parent=self.id):
                node.set_moderators(self._moderators_for_subnodes(node.user))
            self.propagate_path_rebuild = False
        
    
    def invalidate_short_name_and_slug_in_path(self, target=None):
        if not target:
            target = self
        if target.get("references"):
            for reference in target.references:
                from .node import Node
                node = Node.query.get(reference["id"])
                info = dict.copy(node.get(reference["property"]))
                info["short_name"] = self.short_name() # TODO: check if info["parent"] is also needed to update and when. TODO: also info["lang"]
                info["slug"] = self.slug()
                setattr(node, reference["property"], info)
                #self.invalidate_short_name_and_slug_in_path(target=reference) # NOTE: this is not needed because we don't have references to references
                                                                               # AND because references are not showing in the path
        from .node import Node
        Node.query.filter_by(parent=target.get("id")).update({"propagate_slug_and_short_name_rebuild": True, "path": self._path_for_subnodes()})
        
    
    def propagate_rename_if_needed(self):
        from .node import Node
        if self.propagate_slug_and_short_name_rebuild:
            Node.query.filter_by(parent=self.id).update({"propagate_slug_and_short_name_rebuild": True, "path": self._path_for_subnodes()})
            self.propagate_slug_and_short_name_rebuild = False

additional_fields()