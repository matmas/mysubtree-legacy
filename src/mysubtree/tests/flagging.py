from pyquery import PyQuery as pq
from .base import Base

class Flagging(Base):
    
    def vote_as(self, ip_address, nid, undo=False):
        self.logout()
        return self.vote(nid, undo=undo, environ_overrides={"REMOTE_ADDR": ip_address})
    
    def flag_as(self, ip_address, nid, undo=False):
        self.logout()
        if not undo:
            url = "/flag/%s" % nid
        else:
            url = "/flag/%s?undo=true" % nid
        rv = self.client.post(url, follow_redirects=True,
            environ_overrides={"REMOTE_ADDR": ip_address})
        if not undo:
            assert "Thank you for the feedback." in rv.data
    
    def get_num_problematic_of_current_user(self):
        rv = self.client.get(self.url_for("node", lang="en", nodetype="root", nid="en"))
        num_problematic = int(pq(rv.data)("#num-problematic").text() or "0")
        
        rv = self.client.get("/en/problematic")
        self.assertEqual(num_problematic, len(pq(rv.data)(".node")))
        return num_problematic
    
    def get_num_problematic(self, test_user):
        self.logout()
        self.login_test_user(test_user)
        return self.get_num_problematic_of_current_user()
    
    def runTest(self):
        self.register_test_user("1")
        
        # Add item1 as User1
        rv = self.post_node(type="items", parent="en", name="item1")
        item1 = self.get_newest_node_nid(rv.data)
        
        # root
            # sk
            # en
                # item1 (User1)
        
        self.logout()
        #-----------------------------------------------------------------------
        self.register_test_user("2")
        
        # Add item2 as User2
        rv = self.post_node(type="items", parent=item1, name="item2")
        item2 = self.get_newest_node_nid(rv.data)
        
        # root
            # sk
            # en
                # item1 (User1)
                    # item2 (User2)
        
        self.logout()
        #-----------------------------------------------------------------------
        self.register_test_user("spammer")
        
        # Add spam as Userspammer
        rv = self.post_node(type="items", parent=item2, name="spam")
        spam = self.get_newest_node_nid(rv.data)
        
        # root
            # sk
            # en
                # item1 (User1)
                    # item2 (User2)
                        # spam (Userspammer)
        
        self.logout()
        #-----------------------------------------------------------------------
        rv = self.client.post("/flag/%s" % spam, follow_redirects=True,
            environ_overrides={"REMOTE_ADDR": "127.0.0.1"})
        assert "Thank you for the feedback." in rv.data
        
        rv = self.client.post("/flag/%s" % spam, follow_redirects=True,
            environ_overrides={"REMOTE_ADDR": "127.0.0.1"})
        assert "You already sent the feedback." in rv.data
        
        rv = self.client.post("/flag/%s" % spam, follow_redirects=True,
            environ_overrides={"REMOTE_ADDR": "127.0.0.1"}, headers=[('X-Requested-With', 'XMLHttpRequest')])
        assert "You already sent the feedback." not in rv.data
        assert "error" not in rv.data
        
        
        rv = self.client.post("/flag/%s?undo=true" % spam, follow_redirects=True,
            environ_overrides={"REMOTE_ADDR": "127.0.0.1"})
        assert "You undid your feedback." in rv.data
        
        rv = self.client.post("/flag/%s" % spam, follow_redirects=True,
            environ_overrides={"REMOTE_ADDR": "127.0.0.1"})
        assert "Thank you for the feedback." in rv.data
        
        assert self.get_num_problematic(test_user="1") == 1
        assert self.get_num_problematic(test_user="2") == 1
        assert self.get_num_problematic(test_user="spammer") == 1
        
        self.logout()
        #-----------------------------------------------------------------------
        self.login_test_user("1")
        
        # Delete item2
        self.delete_node(item2)
        
        # root
            # sk
            # en
                # item1 (User1)
            # trash
                # item2 (User2)
                    # spam (Userspammer)
        
        
        assert self.get_num_problematic(test_user="1") == 0
        assert self.get_num_problematic(test_user="2") == 1
        assert self.get_num_problematic(test_user="spammer") == 1
        
        self.logout()
        #-----------------------------------------------------------------------
        self.login_test_user("2")
        
        self.restore_node(item2)
        
        # root
            # sk
            # en
                # item1 (User1)
                    # item2 (User2)
                        # spam (Userspammer)
        
        assert self.get_num_problematic(test_user="1") == 1
        assert self.get_num_problematic(test_user="2") == 1
        assert self.get_num_problematic(test_user="spammer") == 1
        
        self.delete_node(spam)
        
        # root
            # sk
            # en
                # item1 (User1)
                    # item2 (User2)
            # trash
                # spam (Userspammer)
        
        assert self.get_num_problematic(test_user="1") == 0
        assert self.get_num_problematic(test_user="2") == 0
        assert self.get_num_problematic(test_user="spammer") == 1
        
        self.logout()
        #-----------------------------------------------------------------------
        self.login_test_user("spammer")
        
        self.restore_node(spam)
        
        # root
            # sk
            # en
                # item1 (User1)
                    # item2 (User2)
                        # spam (Userspammer)
        
        assert self.get_num_problematic(test_user="1") == 1
        
        self.logout()
        #-----------------------------------------------------------------------
        
        # flags 1, votes 0
        
        self.vote_as("127.0.0.2", spam)
        
        # flags 1, votes 1
        
        assert self.get_num_problematic(test_user="1") == 0
        
        self.vote_as("127.0.0.2", spam, undo=True)
        
        # flags 1, votes 0
        
        assert self.get_num_problematic(test_user="1") == 1
        
        self.vote_as("127.0.0.2", spam)
        
        # flags 1, votes 1
        
        assert self.get_num_problematic(test_user="1") == 0
        
        self.vote_as("127.0.0.3", spam)
        
        # flags 1, votes 2
        
        self.vote_as("127.0.0.4", spam)
        
        # flags 1, votes 3
        
        assert self.get_num_problematic(test_user="1") == 0
        
        self.flag_as("127.0.0.5", spam)
        
        # flags 2, votes 3
        
        assert self.get_num_problematic(test_user="1") == 0
        
        self.flag_as("127.0.0.6", spam)
        
        # flags 3, votes 3
        
        assert self.get_num_problematic(test_user="1") == 0
        
        self.flag_as("127.0.0.7", spam)
        
        # flags 4, votes 3
        
        assert self.get_num_problematic(test_user="1") == 1
        
        self.flag_as("127.0.0.7", spam, undo=True)
        
        # flags 3, votes 3
        
        assert self.get_num_problematic(test_user="1") == 0