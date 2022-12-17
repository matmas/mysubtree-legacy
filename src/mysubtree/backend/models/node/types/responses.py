from ..node import Node


class Responses(Node):
    
    __mapper_args__ = {"polymorphic_identity": "responses"}
    
    def __init__(self, user):
        Node.__init__(self)
        self.set_parent(None)
        self.user = user
        
    def is_posting_forbidden(self):
        return True
    
    @staticmethod
    def branching():
        return ["items", "comments", "versions", "edit-suggestions", "log-entries", "votes"]
    
    def hide_user_and_time(self):
        return True
