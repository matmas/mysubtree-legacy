from pyquery import PyQuery as pq
from .base import Base

class UnreadNotifications(Base):
    def get_num_unread(self, html):
        try:
            return int(pq(html)("#num-unread-responses").text())
        except TypeError, ValueError:
            return 0
    
    def runTest(self):
        self.register_test_user("1")
        rv = self.post_node(type="items", parent="en", name="item1")
        item1 = self.get_node_nid(rv.data, slug="item1")
        assert self.get_num_unread(rv.data) == 0
        
        self.logout()
        #-----------------------------------------------------------------------
        self.register_test_user("2")
        
        rv = self.post_node(type="items", parent=item1, name="item2")
        
        self.logout()
        #-----------------------------------------------------------------------
        self.login_test_user("1")
        
        rv = self.get_node(item1)
        assert self.get_num_unread(rv.data) == 1
        rv = self.get_node(item1)
        assert self.get_num_unread(rv.data) == 1
        rv = self.get_nodes(item1, "items")
        assert self.get_num_unread(rv.data) == 0
        
        self.logout()
        #-----------------------------------------------------------------------
        self.login_test_user("2")
        
        num_per_page = self.app.config["NUM_NODES_PER_PAGE"]
        
        for i in range(1, num_per_page + 1): # from 1 to num_per_page
            rv = self.post_node(type="items", parent=item1, name="item%03d" % i)
        
        self.logout()
        #-----------------------------------------------------------------------
        
        rv = self.vote(item1, environ_overrides={"REMOTE_ADDR": "127.0.0.2"})
        assert "Voted sucessfully." in rv.data
        
        #-----------------------------------------------------------------------
        self.login_test_user("1")
        
        # Verify there are 11 unread responses:
        rv = self.get_node(item1)
        assert self.get_num_unread(rv.data) == num_per_page + 1
        
        # Read first 10 responses (1 unread response left):
        rv = self.client.get("/en/responses")
        self.assertEquals(self.get_num_unread(rv.data), 1)
        assert len(pq(rv.data)(".inside")) == num_per_page
        assert len(pq(rv.data)(".reading")) == num_per_page
        
        # Read last 1 response (0 unread responses left):
        rv = self.client.get("/en/responses?offset=10")
        assert self.get_num_unread(rv.data) == 0
        assert len(pq(rv.data)(".inside")) == 2 # there is also the item2 read previously
        assert len(pq(rv.data)(".reading")) == 1
        
        # Reading first 10 responses again:
        rv = self.client.get("/en/responses")
        assert self.get_num_unread(rv.data) == 0
        assert len(pq(rv.data)(".inside")) == num_per_page
        assert len(pq(rv.data)(".reading")) == 0
        
        # Reading last 1 response again:
        rv = self.client.get("/en/responses?offset=10")
        assert self.get_num_unread(rv.data) == 0
        assert len(pq(rv.data)(".inside")) == 2
        assert len(pq(rv.data)(".reading")) == 0
        
