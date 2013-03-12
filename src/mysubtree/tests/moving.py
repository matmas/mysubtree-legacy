from .base import Base

class Moving(Base):
    def runTest(self):
        self.register_test_user("1")
        rv = self.post_node(type="items", parent="en", name="item1")
        item1 = self.get_node_nid(rv.data, slug="item1")
        rv = self.post_node(type="items", parent=item1, name="item2")
        item2 = self.get_node_nid(rv.data, slug="item2")
        rv = self.post_node(type="items", parent=item2, name="item3")
        item3 = self.get_node_nid(rv.data, slug="item3")
        rv = self.post_node(type="items", parent="en", name="item4")
        item4 = self.get_node_nid(rv.data, slug="item4")
        
        self.logout()
        #--- User 2 ------------------------------------------------------------
        self.register_test_user("2")
        
        rv = self.post_node(type="items", parent=item3, name="my item")
        myitem = self.get_node_nid(rv.data, slug="my-item")
        
        self.logout()
        #--- User 1 ------------------------------------------------------------
        self.login_test_user("1")
        
        # root
            # sk
            # en
                # item1
                    # item2
                        # item3
                            # my item
                # item4
        
        # Move item1 into item4:
        rv = self.move_node(item1, item4)
        assert "Moved successfully." in rv.data
        
        # root
            # sk
            # en
                # item4
                    # item1
                        # item2
                            # item3
                                # my item
        
        rv = self.get_node(myitem)
        assert "item4" not in rv.data # not yet propagated
        self.get_nodes(item2, "items") # trigger the propagation
        self.get_nodes(item3, "items") # trigger the propagation
        rv = self.get_node(myitem)
        assert "item4" in rv.data # should be propagated now
        
        # Move my item into en:
        rv = self.move_node(myitem, "en")
        assert "Moved successfully." in rv.data
        
        # root
            # sk
            # en
                # my item
                # item4
                    # item1
                        # item2
                            # item3
        
        # Move my item back into item3:
        rv = self.move_node(myitem, item3)
        assert "You are neither owner nor moderator of that node." in rv.data
        
        self.logout()
        #--- User 2 ------------------------------------------------------------
        self.login_test_user("2")
        
        # Move my item back into item3:
        rv = self.move_node(myitem, item3)
        assert "Moved successfully." in rv.data
        
        # root
            # sk
            # en
                # item4
                    # item1
                        # item2
                            # item3
                                # my item
        
        # Test move_to without move:
        rv = self.client.get("/move-to/%s" % item3, follow_redirects=True)
        # no exception should occur
        
