from pyquery import PyQuery as pq
from .base import Base

class O(Base):
    
    def follow_redirect(self, new_location):
        prefix_to_strip = "http://localhost"
        if new_location.startswith(prefix_to_strip):
            new_location = new_location[len(prefix_to_strip):]
        return self.client.get(new_location)
        
    
    def runTest(self):
        self.register_test_user("1")
        rv = self.post_node(type="items", parent="en", name="item1")
        item1 = self.get_newest_node_nid(rv.data)
        
        rv = self.post_node(type="items", parent="en", name="item2")
        item2 = self.get_newest_node_nid(rv.data)
        
        rv = self.post_node(type="items", parent=item1, name="item1-1")
        item1_1 = self.get_newest_node_nid(rv.data)
        
        rv = self.post_node(type="items", parent=item1, name="item1-2")
        item1_2 = self.get_newest_node_nid(rv.data)
        
        rv = self.post_node(type="items", parent=item1_1, name="item1-1-1")
        item1_1_1 = self.get_newest_node_nid(rv.data)
        
        rv = self.post_node(type="items", parent=item1_1, name="item1-1-2")
        item1_1_2 = self.get_newest_node_nid(rv.data)
        
        rv = self.post_node(type="items", parent=item1_1_1, name="item1-1-1-1")
        item1_1_1_1 = self.get_newest_node_nid(rv.data)
        
        rv = self.post_node(type="items", parent=item1_1_1, name="item1-1-1-2")
        item1_1_1_2 = self.get_newest_node_nid(rv.data)
        
        # root
            # sk
            # en
                # item1
                    # item1-1
                        # item1-1-1
                            # item1-1-1-1
                                # item1-1-1-1-1
                                # item1-1-1-1-2
                            # item1-1-1-2
                        # item1-1-2
                    # item1-2
                # item2
        
        # Test if slug redirects keep the o:
        rv = self.client.get(self.url_for("node", lang="en", nodetype="items", nid=item1_1_1_1, o="nn"))
        assert rv.location.endswith("o=nn")
        
        rv = self.client.get(self.url_for("node", lang="en", nodetype="items", nid=item1_1_1, type="items", o=""), follow_redirects=True)
        all_nodes_html = pq(rv.data)(".all-nodes").html()
        assert item1 not in all_nodes_html
        assert item2 not in all_nodes_html
        assert item1_1 not in all_nodes_html
        assert item1_2 not in all_nodes_html
        
        rv = self.client.get(self.url_for("node", lang="en", nodetype="items", nid=item1_1_1, type="items", o="n"), follow_redirects=True)
        all_nodes_html = pq(rv.data)(".all-nodes").html()
        assert item1 not in all_nodes_html
        assert item2 not in all_nodes_html
        assert item1_1 in all_nodes_html
        assert item1_2 not in all_nodes_html
        
        rv = self.client.get(self.url_for("node", lang="en", nodetype="items", nid=item1_1_1, type="items", o="nn"), follow_redirects=True)
        all_nodes_html = pq(rv.data)(".all-nodes").html()
        assert item1 in all_nodes_html
        assert item2 not in all_nodes_html
        assert item1_1 in all_nodes_html
        assert item1_2 in all_nodes_html
        
        rv = self.client.get(self.url_for("node", lang="en", nodetype="items", nid=item1_1_1, type="items", o="nnn"), follow_redirects=True)
        all_nodes_html = pq(rv.data)(".all-nodes").html()
        assert item1 in all_nodes_html
        assert item2 in all_nodes_html
        assert item1_1 in all_nodes_html
        assert item1_2 in all_nodes_html
        
        rv = self.client.get(self.url_for("node", lang="en", nodetype="items", nid=item1_1_1, o="nnn"), follow_redirects=True)
        all_nodes_html = pq(rv.data)(".all-nodes").html()
        assert item1 in all_nodes_html
        assert item2 in all_nodes_html
        assert item1_1 in all_nodes_html
        assert item1_2 in all_nodes_html
        
        
