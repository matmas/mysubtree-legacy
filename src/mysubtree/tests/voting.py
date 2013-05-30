from flask import request
from pyquery import PyQuery as pq
from lib import time
from .base import Base

class Voting(Base):
    def runTest(self):
        #--- User 1 ------------------------------------------------------------
        self.register_test_user("1")
        
        # Post item
        rv = self.post_node(type="items", parent="en", name="item1")
        item1 = self.get_newest_node_nid(rv.data)
        
        # root
            # en
                # item1 (User1)
        
        # Try to vote for it as author:
        rv = self.vote("items", item1)
        assert "This node is created by your IP address. The author is not allowed to vote for his node. Wait for the likes from others." in rv.data
        assert "<span class='vote-indicator'>%d</span>" % 0 in rv.data
        
        self.logout()
        #--- User 2 ------------------------------------------------------------
        self.register_test_user("2")
        
        # Vote for it from different IP address and different user:
        rv = self.vote("items", item1, environ_overrides={"REMOTE_ADDR": "127.0.0.2"})
        assert "Voted sucessfully." in rv.data
        
        # root
            # en
                # item1 (User1)
                    # +1 (User2 (127.0.0.2))
        
        # Check that the IP address is hidden and user name is shown:
        rv = self.get_nodes("items", item1, "votes")
        assert "User2" in rv.data
        assert "127.0.0.2" not in rv.data
        assert "<span class='vote-indicator'>%d</span>" % 1 in rv.data
        
        # Try to vote again from the same IP address:
        rv = self.vote("items", item1, environ_overrides={"REMOTE_ADDR": "127.0.0.2"})
        assert "You like it already." in rv.data
        assert "<span class='vote-indicator'>%d</span>" % 1 in rv.data
        
        self.logout()
        #--- User 2 ------------------------------------------------------------
        self.register_test_user("3")
        
        # Try to vote again from the same IP address (while being logged off):
        rv = self.vote("items", item1, environ_overrides={"REMOTE_ADDR": "127.0.0.2"})
        assert "From your IP address has been voted +1 for it." in rv.data
        assert "<span class='vote-indicator'>%d</span>" % 1 in rv.data
        
        # Try to undo vote from the same IP as the previous voter but logged in as different user:
        rv = self.vote("items", item1, undo=True, environ_overrides={"REMOTE_ADDR": "127.0.0.2"})
        assert "From your IP address has been voted +1 for it by another user. Undo is not possible." in rv.data
        assert "<span class='vote-indicator'>%d</span>" % 1 in rv.data
        
        self.logout()
        #-----------------------------------------------------------------------
        
        # Vote while logged off:
        rv = self.vote("items", item1, environ_overrides={"REMOTE_ADDR": "127.0.0.3"})
        assert "Voted sucessfully." in rv.data
        assert "<span class='vote-indicator'>%d</span>" % 2 in rv.data
        
        # root
            # en
                # item1 (User1)
                    # +1 (User2 (127.0.0.2))
                    # +1 (127.0.0.3)
        
        # Check IP-address only vote:
        rv = self.get_nodes("items", item1, "votes")
        assert "127.0.0.3" in rv.data
        
        #--- User 2 ------------------------------------------------------------
        self.login_test_user("2")
        
        # Try to undo vote when logged in that was cast while logged off:
        rv = self.vote("items", item1, undo=True, environ_overrides={"REMOTE_ADDR": "127.0.0.3"})
        assert "From your IP address has been voted +1 for it while being logged off. Log off and try again." in rv.data
        
        self.logout()
        #-----------------------------------------------------------------------
        
        # Undo the vote immediately:
        rv = self.vote("items", item1, undo=True, environ_overrides={"REMOTE_ADDR": "127.0.0.3"})
        assert "You sucessfully undid your vote." in rv.data
        assert "<span class='vote-indicator'>%d</span>" % 1 in rv.data
        rv = self.get_nodes("items", item1, "votes")
        assert "127.0.0.3" not in rv.data
        
        # root
            # en
                # item1 (User1)
                    # +1 (User2 (127.0.0.2))
        
        # Vote again:
        rv = self.vote("items", item1, environ_overrides={"REMOTE_ADDR": "127.0.0.3"})
        assert "Voted sucessfully." in rv.data
        assert "<span class='vote-indicator'>%d</span>" % 2 in rv.data
        
        # root
            # en
                # item1 (User1)
                    # +1 (User2 (127.0.0.2))
                    # +1 (127.0.0.3)
        
        time.move_forward(minutes=30)
        
        # Undo the vote after 30 minutes:
        rv = self.vote("items", item1, undo=True, environ_overrides={"REMOTE_ADDR": "127.0.0.3"})
        assert "You sucessfully undid your vote." in rv.data
        assert "<span class='vote-indicator'>%d</span>" % 1 in rv.data
        rv = self.get_nodes("items", item1, "votes")
        assert "127.0.0.3" in rv.data # It should remain
        
        # root
            # en
                # item1 (User1)
                    # +1 (User2 (127.0.0.2))
                    # +1 (127.0.0.3)
                    # -1 (127.0.0.3)
        
        # Try to undo the vote again:
        rv = self.vote("items", item1, undo=True, environ_overrides={"REMOTE_ADDR": "127.0.0.3"})
        assert "No like to undo." in rv.data
        
        # Vote again:
        rv = self.vote("items", item1, environ_overrides={"REMOTE_ADDR": "127.0.0.3"})
        assert "Voted sucessfully." in rv.data
        assert "<span class='vote-indicator'>%d</span>" % 2 in rv.data
        
        # root
            # en
                # item1 (User1)
                    # +1 (User2 (127.0.0.2))
                    # +1 (127.0.0.3)
                    # -1 (127.0.0.3)
                    # +1 (127.0.0.3)
        
        rv = self.get_nodes("items", item1, "votes")
        votenodes = pq(rv.data)(".inside")
        
        num_plus1 = 0
        num_minus1 = 0
        for votenode in votenodes:
            if "+1" in pq(votenode).html():
                num_plus1 += 1
            elif "-1" in pq(votenode).html():
                num_minus1 += 1
            else:
                pass # parent node
        assert num_plus1 == 3  # one from 127.0.0.2 and two from 127.0.0.3 (one valid and one undone)
        assert num_minus1 == 1 # one undo from 127.0.0.3
        
        self.logout()
        
        # Try to undo nonexistent vote:
        rv = self.vote("items", item1, undo=True, environ_overrides={"REMOTE_ADDR": "127.0.0.4"})
        assert "No like to undo." in rv.data
        
        # Try to undo nonexistent vote with javascript:
        rv = self.vote("items", item1, undo=True, environ_overrides={"REMOTE_ADDR": "127.0.0.4"}, headers=[('X-Requested-With', 'XMLHttpRequest')])
        assert "No like to undo." not in rv.data
        assert "error" not in rv.data
        