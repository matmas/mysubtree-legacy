from datetime import timedelta
from lib.time import utcnow
from mysubtree.backend import common
from mysubtree.db import db
from mysubtree.web.user import get_user_node
from mysubtree.backend.live.live import on_node_update
from mysubtree.backend.models.node.types.all import get_all_types


def additional_fields():
    for type in get_all_types():
        setattr(NodeActivity, "activity_%s" % type, db.Column(db.DateTime()))


class NodeActivity:
    
    activity = db.Column(db.DateTime())
    
    def __init__(self):
        self.activity = utcnow()
    
    def is_activity_propagation_forbidden(self):
        return False
    
    def propagate_activity_upwards(self):
        if self.is_activity_propagation_forbidden():
            return
        
        branching_type = self.type
        now = utcnow()

        def update_activity(id, type, branching_type):
            activity_type = "activity_%s" % branching_type
            on_node_update(id)
            return db.session.connection().execute(
                "UPDATE node "
                "SET \""+activity_type+"\" = %(now_minus_1sec)s, activity = %(now)s "
                "WHERE id = %(id)s AND type = %(type)s AND (\""+activity_type+"\" < %(now_minus_1sec)s OR \""+activity_type+"\" IS NULL)",
                {
                    "id": id,
                    "type": type,
                    "now": now,
                    "now_minus_1sec": now - timedelta(seconds=1),
                }
            )
        
        # user node:
        update_activity(get_user_node(), "users", branching_type)

        # parent nodes:
        for ancestor in reversed(self.path):
            if update_activity(ancestor["id"], ancestor["type"], branching_type).rowcount == 0: # updating too fast
                break
            branching_type = ancestor["type"]
    
    def get_activity(self, branching_type):
        return self.get("activity_%s" % branching_type)


additional_fields()
