from pyquery import PyQuery as pq
from lib import time
from .base import Base


class Decrementer(Base):
    
    def get_stats(self, nid, type, nids, sort_type):
        rv = self.get_nodes("items", nid, type, sort_type)
        sorting = self.get_sorting(rv.data)
        return self.get_votes(nids, rv.data) + [True if sort_type in sorting else False]
    
    def get_votes(self, nid_or_nids, html):
        if type(nid_or_nids) == str:
            nid = nid_or_nids
            return int(pq(html)("#" + nid).find(".vote-indicator").text())
        else:
            nids = nid_or_nids
            return [self.get_votes(nid, html) for nid in nids]
    
    def get_sorting(self, html):
        return pq(html)(".sort").html() or ""
    
    def get_sorting_count(self, html):
        return len(pq(html)(".sort > li"))
    
    def check_sorting(self, html, items):
        sorting = self.get_sorting(html)
        prev_sum_abs_votes = 0;
        for sort_type in ["1day", "1week", "1month", "1year", "alltime", "activity"]:
            rv = self.client.get(self.url_for("node", nodetype="root", nid="en", type="items", sort=sort_type))
            sum_abs_votes = 0
            for item in items:
                votes = self.get_votes(item, rv.data)
                sum_abs_votes += abs(votes)
            
            if prev_sum_abs_votes == sum_abs_votes:
                assert sort_type not in sorting
            else:
                assert sort_type in sorting
            
            prev_sum_abs_votes = sum_abs_votes
            
    def runTest(self):
        self.register_test_user("1")
        rv = self.post_node(type="items", parent="en", name="item1")
        item1 = self.get_newest_node_nid(rv.data)
        rv = self.post_node(type="items", parent="en", name="item2")
        item2 = self.get_newest_node_nid(rv.data)
        rv = self.post_node(type="items", parent="en", name="item3")
        item3 = self.get_newest_node_nid(rv.data)
        
        items = [item1, item2, item3]
        
        self.logout()
        #-----------------------------------------------------------------------
        
        rv = self.client.get(self.url_for("node", nodetype="root", nid="en", type="items"))
        self.check_sorting(rv.data, [item1, item2, item3])
        assert self.get_votes(item1, rv.data) == 0
        assert self.get_sorting(rv.data) == ""
        
        rv = self.vote("items", item1, environ_overrides={"REMOTE_ADDR": "127.0.0.2"})
        
        self.assertEquals(self.get_stats("en", "items", items, ""),        [1, 0, 0, True])
        self.assertEquals(self.get_stats("en", "items", items, "1day"),    [1, 0, 0, True])
        self.assertEquals(self.get_stats("en", "items", items, "1week"),   [1, 0, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "1month"),  [1, 0, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "1year"),   [1, 0, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "alltime"), [1, 0, 0, False])
        
        time.move_forward(days=1)
        
        self.assertEquals(self.get_stats("en", "items", items, ""),        [1, 0, 0, True])
        self.assertEquals(self.get_stats("en", "items", items, "1day"),    [0, 0, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "1week"),   [1, 0, 0, True])
        self.assertEquals(self.get_stats("en", "items", items, "1month"),  [1, 0, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "1year"),   [1, 0, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "alltime"), [1, 0, 0, False])
        
        time.move_forward(days=7 - 1)
        
        self.assertEquals(self.get_stats("en", "items", items, ""),        [1, 0, 0, True])
        self.assertEquals(self.get_stats("en", "items", items, "1day"),    [0, 0, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "1week"),   [0, 0, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "1month"),  [1, 0, 0, True])
        self.assertEquals(self.get_stats("en", "items", items, "1year"),   [1, 0, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "alltime"), [1, 0, 0, False])
        
        time.move_forward(days=30 - 7)
        
        self.assertEquals(self.get_stats("en", "items", items, ""),        [1, 0, 0, True])
        self.assertEquals(self.get_stats("en", "items", items, "1day"),    [0, 0, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "1week"),   [0, 0, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "1month"),  [0, 0, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "1year"),   [1, 0, 0, True])
        self.assertEquals(self.get_stats("en", "items", items, "alltime"), [1, 0, 0, False])
        
        time.move_forward(days=365 - 30)
        
        self.assertEquals(self.get_stats("en", "items", items, ""),        [1, 0, 0, True])
        self.assertEquals(self.get_stats("en", "items", items, "1day"),    [0, 0, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "1week"),   [0, 0, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "1month"),  [0, 0, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "1year"),   [0, 0, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "alltime"), [1, 0, 0, True])
        
        
        rv = self.vote("items", item2, environ_overrides={"REMOTE_ADDR": "127.0.0.3"})
        
        self.assertEquals(self.get_stats("en", "items", items, ""),        [1, 1, 0, True])
        self.assertEquals(self.get_stats("en", "items", items, "1day"),    [0, 1, 0, True])
        self.assertEquals(self.get_stats("en", "items", items, "1week"),   [0, 1, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "1month"),  [0, 1, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "1year"),   [0, 1, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "alltime"), [1, 1, 0, True])
        
        time.move_forward(days=30)
        
        self.assertEquals(self.get_stats("en", "items", items, ""),        [1, 1, 0, True])
        self.assertEquals(self.get_stats("en", "items", items, "1day"),    [0, 0, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "1week"),   [0, 0, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "1month"),  [0, 0, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "1year"),   [0, 1, 0, True])
        self.assertEquals(self.get_stats("en", "items", items, "alltime"), [1, 1, 0, True])
        
        rv = self.vote("items", item2, undo=True, environ_overrides={"REMOTE_ADDR": "127.0.0.3"})
        
        self.assertEquals(self.get_stats("en", "items", items, ""),        [1, 0, 0, True])
        self.assertEquals(self.get_stats("en", "items", items, "1day"),    [0, -1, 0, True])
        self.assertEquals(self.get_stats("en", "items", items, "1week"),   [0, -1, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "1month"),  [0, -1, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "1year"),   [0, 0, 0, True])
        self.assertEquals(self.get_stats("en", "items", items, "alltime"), [1, 0, 0, True])
        
        time.move_forward(days=7)
        
        self.assertEquals(self.get_stats("en", "items", items, ""),        [1, 0, 0, True])
        self.assertEquals(self.get_stats("en", "items", items, "1day"),    [0, 0, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "1week"),   [0, 0, 0, False])
        self.assertEquals(self.get_stats("en", "items", items, "1month"),  [0, -1, 0, True])
        self.assertEquals(self.get_stats("en", "items", items, "1year"),   [0, 0, 0, True])
        self.assertEquals(self.get_stats("en", "items", items, "alltime"), [1, 0, 0, True])
        