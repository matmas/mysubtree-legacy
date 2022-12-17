from .base import Base


class Root(Base):
    def runTest(self):
        rv = self.client.get("/languages/en", follow_redirects=True)
        assert "root" in rv.data
        assert "trash" in rv.data
        
        rv = self.client.get("/en/root/trash", follow_redirects=True)
        assert rv.status_code == 200
        assert "Nodes in trash will be permanently deleted after 30 days." in rv.data