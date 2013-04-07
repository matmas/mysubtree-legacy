from pyquery import PyQuery as pq
from .base import Base

class Editing(Base):
    
    def edit(self, nid, new_body, version):
        return self.client.post("/edit/unknown-%s" % nid, data=dict(body=new_body, version=version), follow_redirects=True)
    
    def runTest(self):
        #--- User 1 ------------------------------------------------------------
        self.register_test_user("1")
        
        # Post an item:
        rv = self.post_node(type="items", parent="en", name="item1")
        assert "Posted successfully." in rv.data
        item1 = self.get_node_nid(rv.data, slug="item1")
        
        # Post a comment:
        rv = self.post_node(type="comments", parent=item1, body="comment1")
        assert "Posted successfully." in rv.data
        comment1 = self.get_newest_node_nid(rv.data)
        
        # Edit an item:
        rv = self.edit(item1, "item1 description", version=2)
        assert "Saved successfully." in rv.data
        assert "item1 description" in rv.data
        
        # Edit a comment:
        rv = self.edit(comment1, "comment1 (edited)", version=2)
        assert "Saved successfully." in rv.data
        assert "comment1 (edited)" in rv.data
        
        self.logout()
        #--- User 2 ------------------------------------------------------------
        self.register_test_user("2")
        
        # Suggest edit 1:
        rv = self.edit(item1, "suggested edit 1", version=3)
        assert "Posted successfully." in rv.data # edit suggestion
        rv = self.get_nodes(item1, "edit-suggestions")
        edit1 = self.get_newest_node_nid(rv.data)
        
        # Suggest edit 2:
        rv = self.edit(item1, "suggested edit 2", version=3)
        assert "Posted successfully." in rv.data # edit suggestion
        rv = self.get_nodes(item1, "edit-suggestions")
        edit2 = self.get_newest_node_nid(rv.data)
                
        # Suggest edit 1-1:
        rv = self.edit(edit2, "suggested edit 1-1", version=4)
        assert "Posted successfully." in rv.data # edit suggestion
        
        self.logout()
        #--- User 1 ------------------------------------------------------------
        self.login_test_user("1")
        
        # Accept suggested edit 1
        rv = self.client.post("/accept/unknown-%s" % edit1, follow_redirects=True)
        assert "Accepted sucessfully." in rv.data
        
        # Accept suggested edit 1 again
        rv = self.client.post("/accept/unknown-%s" % edit1, follow_redirects=True)
        assert "This edit suggestion is already accepted." in rv.data
        
        # Accept suggested edit 2
        rv = self.client.post("/accept/unknown-%s" % edit2, follow_redirects=True)
        assert "This edit suggestion is not possible to accept anymore because a different one was accepted." in rv.data
        
        # Check the versions:
        rv = self.get_nodes(item1, "versions")
        assert len(pq(rv.data)(".permalink")) == 4 # original + two accepted edit suggestions + parent node