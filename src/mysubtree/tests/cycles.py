from .base import Base

class Cycles(Base):
    def runTest(self):
        self.register_test_user("1")
        rv = self.post_node(type="items", parent="en", name="item1")
        item1 = self.get_newest_node_nid(rv.data)
        rv = self.post_node(type="items", parent="en", name="item2")
        item2 = self.get_newest_node_nid(rv.data)
        
        # root
            # sk
            # en
                # item1
                # item2
        
        rv = self.move_node(item2, item1)
        assert "Moved successfully." in rv.data
        
        # root
            # sk
            # en
                # item1
                    # item2
        
        rv = self.move_node(item1, item2)
        assert "Could not move to inside of itself." in rv.data
        
        # Move back:
        rv = self.move_node(item2, "en")
        
        # root
            # sk
            # en
                # item1
                # item2
        
        rv = self.post_node(type="items", parent=item1, name="item1-1")
        item1_1 = self.get_newest_node_nid(rv.data)
        rv = self.post_node(type="items", parent=item2, name="item2-2")
        item2_2 = self.get_newest_node_nid(rv.data)
        
        # root
            # sk
            # en
                # item1
                    # item1-1
                # item2
                    # item2-2
        
        rv = self.move_node(item2, item1_1)
        assert "Moved successfully." in rv.data
        
        # root
            # sk
            # en
                # item1
                    # item1-1
                        # item2
                            # item2-2
        
        rv = self.move_node(item1, item2_2)
        assert "Could not move to inside of itself." in rv.data
        
        # Move back:
        rv = self.move_node(item2, "en")
        assert "Moved successfully." in rv.data
        
        # root
            # sk
            # en
                # item1
                    # item1-1
                # item2
                    # item2-2
        
        rv = self.post_node(type="items", parent=item1_1, name="item1-1-1")
        item1_1_1 = self.get_newest_node_nid(rv.data)
        rv = self.post_node(type="items", parent=item2_2, name="item2-2-2")
        item2_2_2 = self.get_newest_node_nid(rv.data)
        
        # root
            # sk
            # en
                # item1
                    # item1-1
                        # item1-1-1
                # item2
                    # item2-2
                        # item2-2-2
        
        rv = self.move_node(item2, item1_1_1)
        assert "Moved successfully." in rv.data
        
        # root
            # sk
            # en
                # item1
                    # item1-1
                        # item1-1-1
                            # item2
                                # item2-2
                                    # item2-2-2
        
        rv = self.move_node(item1, item2_2_2)
        assert "Moved successfully." in rv.data
        
        # root
            # sk
            # en
                # item1------------------------------\
                    # item1-1                        |
                        # item1-1-1                  |
                            # item2                  |
                                # item2-2            |
                                    # item2-2-2------/
        #rv = self.get_node("items", item1)
        rv = self.get_node("items", item1_1)
        rv = self.get_node("items", item1_1_1)
        rv = self.get_node("items", item2)
        #rv = self.get_node("items", item2_2)
        #rv = self.get_node("items", item2_2_2)
        
        assert "trash" in rv.data # in breadcrumb