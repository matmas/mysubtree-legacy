from .base import Base

class Adding(Base):
    def runTest(self):
        rv = self.get_node("en")
        assert "new item" not in rv.data # without link to posting new items
        assert "1 item" not in rv.data # assume no items in there
        
        # Try to post logged out:
        rv = self.post_node(type="items", parent="en", name="item")
        assert "You must be logged in to post anything." in rv.data
        
        self.register_test_user("1")
        
        # Try to post logged in:
        rv = self.post_node(type="items", parent="en", name="<test item 1>")
        assert "Posted successfully." in rv.data
        assert "1 item" in rv.data # one item appeared
        item1 = self.get_node_nid(rv.data, slug="test-item-1")
        rv = self.get_node(item1)
        assert "&lt;test item 1&gt;" in rv.data
        
        # root
            # sk
            # en
                # <test item1>
        
        # Post another item beneath the previous one:
        rv = self.post_node(type="items", parent=item1, name="item2")
        assert "Posted successfully." in rv.data
        item2 = self.get_node_nid(rv.data, slug="item2")
        
        # root
            # sk
            # en
                # <test item1>
                    # item2
        
        # Post another item beneath the previous one:
        rv = self.post_node(type="items", parent=item2, name="item3")
        assert "Posted successfully." in rv.data
        item3 = self.get_node_nid(rv.data, slug="item3")
        
        # root
            # sk
            # en
                # <test item1>
                    # item2
                        # item3
        
        # See if the breadcrumb is correct:
        rv = self.get_node(item3)
        assert all(name in rv.data for name in ["root", "&lt;test item 1&gt;", "item2"]) # rough check