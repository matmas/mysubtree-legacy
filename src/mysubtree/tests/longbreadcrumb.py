from .base import Base

class LongBreadcrumb(Base):
    def runTest(self):
        self.register_test_user("1")
        
        MAX_PATH_SIZE = 10
        next_parent = "en"
        
        for i in xrange(MAX_PATH_SIZE + 3):
            rv = self.post_node(type="items", parent=next_parent, name="item number %03d" % i)
            next_parent = self.get_newest_node_nid(rv.data)
            if i < MAX_PATH_SIZE + 2:
                assert "item number 000" in rv.data
            else:
                assert "item number 000" not in rv.data
        
        # root
            # sk
            # en
                # item number 000
                    # item number 001
                        # item number 002
                            # ...
                                # item number 012
