from pyquery import PyQuery as pq
from .base import Base


class Deleting(Base):
    def runTest(self):
        self.register_test_user("1")
        
        # Add item1:
        rv = self.post_node(type="items", parent="en", name="item1")
        item1 = self.get_newest_node_nid(rv.data)
        
        # Delete item1:
        rv = self.delete_node(item1)
        assert "Deleted successfully." in rv.data
        
        # Try to delete item1 again:
        rv = self.delete_node(item1)
        assert "It is already deleted." in rv.data
        
        # Check that item1 is in trash:
        rv = self. get_node("items", item1)
        assert "trash" in pq(rv.data)(".breadcrumb").html()
        
        self.logout()
        #-----------------------------------------------------------------------
        self.register_test_user("2")
        
        # Try to restore item1 from trash as different user:
        rv = self.restore_node(item1)
        assert "You are neither owner nor moderator of that node." in rv.data
        
        self.logout()
        #-----------------------------------------------------------------------
        self.login_test_user("1")
        
        # Restore item1 from trash:
        rv = self.restore_node(item1)
        assert "Restored successfully." in rv.data
        
        # Check that item1 is *not* in trash:
        rv = self. get_node("items", item1)
        assert "trash" not in pq(rv.data)(".breadcrumb").html()
