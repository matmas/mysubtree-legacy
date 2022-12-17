from .base import Base


class Paging(Base):
    def runTest(self):
        self.register_test_user("1")
        
        num_per_page = self.app.config["NUM_NODES_PER_PAGE"]
        
        for i in range(1, num_per_page + 2):  # from 1 to num_per_page + 1 (inclusive)
            rv = self.post_node(type="items", parent="en", name="item%03d" % i)
            
            if i >= 1 and i <= num_per_page:
                for j in range(1, i + 1):  # from 1 to i (inclusive)
                    assert "item%03d" % j in rv.data
            else:
                #print rv.data
                assert "item%03d" % 1 not in rv.data
