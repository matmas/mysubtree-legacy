from .base import Base

class Renaming(Base):
    def runTest(self):
        self.register_test_user("1")
        
        rv = self.post_node(type="items", parent="en", name="<test item 1>")
        item1 = self.get_node_nid(rv.data, slug="test-item-1")
        rv = self.post_node(type="items", parent=item1, name="item2")
        item2 = self.get_node_nid(rv.data, slug="item2")
        rv = self.post_node(type="items", parent=item2, name="item3")
        item3 = self.get_node_nid(rv.data, slug="item3")
        
        # root
            # sk
            # en
                # <test item1>
                    # item2
                        # item3
        
        # Rename item1
        rv = self.rename_node(item1, "item1 (new name)")
        assert "Renamed successfully." in rv.data
        assert "&lt;test item 1&gt;" not in rv.data
        assert "item1 (new name)" in rv.data
        
        # root
            # sk
            # en
                # item1 (new name)
                    # item2
                        # item3
        
        rv = self.get_node(item3)
        assert "item1 (new name)" not in rv.data # not yet propagated
        
        self.get_node("%s/items" % item2) # trigger the propagation
        rv = self.get_node(item3)
        assert "item1 (new name)" in rv.data # should be propagated now
        
        self.logout()
        #--- User 2 ------------------------------------------------------------
        self.register_test_user("2")
        
        # Try to rename node of user1:
        rv = self.rename_node(item1, "another name")
        assert "You are neither owner nor moderator of that node." in rv.data
        
        # Post something:
        rv = self.post_node(type="items", parent=item3, name="my item")
        myitem = self.get_node_nid(rv.data, slug="my-item")
        
        # root
            # sk
            # en
                # item1 (new name)
                    # item2
                        # item3
                            # my item
        
        self.logout()
        #--- User 1 ------------------------------------------------------------
        self.login_test_user("1")
        
        # Try to rename node of user2:
        rv = self.rename_node(myitem, "your item")
        assert "Renamed successfully." in rv.data
        assert "my item" not in rv.data
        assert "your item" in rv.data
        youritem = myitem
        
        # root
            # sk
            # en
                # item1 (new name)
                    # item2
                        # item3
                            # your item
        
        # Move youritem somewhere
        self.move_node(youritem, "en")
        
        # Log entry gets greated: Moved item3 -> en
        rv = self.get_nodes(youritem, "log-entries")
        assert "item3" in rv.data
        assert "item3 (new name)" not in rv.data
        
        # Rename item3:
        rv = self.rename_node(item3, "item3 (new name)")
        assert "Renamed successfully." in rv.data
        
        # Log entry gets updated: Moved item3 (new name) -> en
        rv = self.get_nodes(youritem, "log-entries")
        assert "item3 (new name)" in rv.data
