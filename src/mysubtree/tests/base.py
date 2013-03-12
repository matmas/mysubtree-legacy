import re
import unittest
from werkzeug.contrib.profiler import ProfilerMiddleware
from mysubtree.web.app import app
from mysubtree.db import db, autoimport_and_init_db

class Base(unittest.TestCase):

    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://mysubtree-test:mysubtree-test@localhost/mysubtree-test?unix_socket=/var/run/mysqld/mysqld.sock"
        app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost"
        #app.config["SQLALCHEMY_ECHO"] = True
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['CACHE_TYPE'] = "simple"
        
        #app.wsgi_app = ProfilerMiddleware(app.wsgi_app, open("profiler.log", "w"))
        
        self.app = app
        self.client = app.test_client()
        
        # drop all tables in database:
        if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgresql"):
            db.session.connection().execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public; COMMIT;")
        elif app.config["SQLALCHEMY_DATABASE_URI"].startswith("mysql"):
            for table in db.session.connection().execute("SHOW TABLES"):
                db.session.connection().execute("SET FOREIGN_KEY_CHECKS = 0")
                db.session.connection().execute("DROP TABLE IF EXISTS %s" % table[0])
                db.session.connection().execute("SET FOREIGN_KEY_CHECKS = 1")
        
        autoimport_and_init_db()

    def tearDown(self):
        pass
    
    #---------------------------------------------------------------------------
    
    def create_account(self, email, name, password):
        # Create account:
        return self.client.post("/en/create-account", data=dict(
            email=email,
            name=name,
            password=password,
            password_again=password,
            agree="yes"
        ), follow_redirects=True)
    
    def get_verification_link(self, html):
        message = "Use the following link within 24 hours to complete your account creation:"
        assert message in html
        i = html.find(message) + len(message)
        verification_link = html[i:html.find("<", i)].strip()
        verification_link = verification_link[len("http://localhost"):]
        assert verification_link.startswith("/en/verify/")
        assert len(verification_link) == len("/en/verify/") + 10
        return verification_link
    
    def register(self, email, name, password):
        rv = self.create_account(email, name, password)
        verification_link = self.get_verification_link(rv.data)
        rv = self.client.get(verification_link, follow_redirects=True)
    
    def login(self, email, password):
        return self.client.post('/en/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)
    
    def logout(self):
        return self.client.get('/en/logout', follow_redirects=True)
    
    def register_test_user(self, number):
        self.register(email="user%s@example.com" % number, name="User%s" % number, password="CommonPassword")
    
    def login_test_user(self, number):
        self.login(email="user%s@example.com" % number, password="CommonPassword")
    
    #---------------------------------------------------------------------------
    
    def post_node(self, type, parent, **kwargs):
        return self.client.post("/post/%s/to/unknown-%s" % (type, parent), data=kwargs, follow_redirects=True)
    
    def get_node(self, nid):
        return self.client.get("/en/nodes/unknown-%s" % nid, follow_redirects=True)
    
    def get_nodes(self, nid, type, sort=None):
        url_suffix = "?sort=%s" % sort if sort else ""
        return self.client.get("/en/branches/unknown-%s/%s%s" % (nid, type, url_suffix), follow_redirects=True)
    
    def get_node_nid(self, html, slug):
        finder = re.compile("""<a class=["'][^"']*["'] href=["']/en/nodes/[^-"]*-([^/"]*)/%s["']""" % slug).finditer(html)
        node_nid = finder.next().groups()[0]
        return node_nid
    
    def move_node(self, nid, target_nid):
        rv = self.client.post("/move/unknown-%s" % nid, follow_redirects=True)
        assert "You may now paste the node somewhere." in rv.data
        return self.client.post("/move-to/unknown-%s" % target_nid, follow_redirects=True)
        #return self.client.post("/move/unknown-%s" % nid, data=dict(url="/en/nodes/unknown-%s" % target_nid), follow_redirects=True)
    
    def rename_node(self, nid, new_name):
        return self.client.post("/rename/unknown-%s" % nid, data=dict(name=new_name), follow_redirects=True)
    
    def vote(self, nid, undo=False, **kwargs):
        if not undo:
            return self.client.post("/vote/unknown-%s" % nid, follow_redirects=True, **kwargs)
        else:
            return self.client.post("/vote/unknown-%s?undo=true" % nid, follow_redirects=True, **kwargs)
    
    def delete_node(self, nid):
        return self.client.post("/delete/unknown-%s" % nid, follow_redirects=True)
    
    def restore_node(self, nid):
        return  self.client.post("/restore/unknown-%s" % nid, follow_redirects=True)
    
