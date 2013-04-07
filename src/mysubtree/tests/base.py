import re
import unittest
from flask import url_for
from werkzeug.contrib.profiler import ProfilerMiddleware
from pyquery import PyQuery as pq
from mysubtree.web.app import app
from mysubtree.db import db, autoimport_and_init_db

class Base(unittest.TestCase):

    def setUp(self):
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
    
    def follow_redirect(self, new_location):
        prefix_to_strip = "http://localhost"
        if new_location.startswith(prefix_to_strip):
            new_location = new_location[len(prefix_to_strip):]
        return self.client.get(new_location)
    
    def url_for(self, endpoint, **kwargs):
        with self.app.test_request_context() as c:
            url = url_for(endpoint, **kwargs)
        return url
    
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
        return self.client.post("/post/%s/to/%s" % (type, parent), data=kwargs, follow_redirects=True)
    
    def get_node(self, type, nid):
        return self.client.get("/en/%s/%s" % (type, nid), follow_redirects=True)
        #return self.client.get(url_for("node", lang="en", nodetype=nodetype, nid=nid), follow_redirects=True)
    
    def get_nodes(self, nodetype, nid, type, sort=None):
        return self.client.get(self.url_for("node", lang="en", nodetype=nodetype, nid=nid, type=type, sort=sort), follow_redirects=True)
    
    def get_node_nid(self, html, type, slug):
        finder = re.compile("""<a class=["'][^"']*["'] href=["']/en/%s/[^-"]*-([^-"]*)-%s["']""" % (type, slug)).finditer(html)
        node_nid = finder.next().groups()[0]
        return node_nid
    
    def get_newest_node_nid(self, html):
        node_nid = pq(html)(".nodes > .node .nodes > .node").eq(0).children(".inside").attr("id")
        return node_nid
    
    def move_node(self, nid, target_nid):
        rv = self.client.post("/move/%s" % nid, follow_redirects=True)
        assert "You may now paste the node somewhere." in rv.data
        return self.client.post("/move-to/%s" % target_nid, follow_redirects=True)
        #return self.client.post("/move/%s" % nid, data=dict(url="/en/nodes/%s" % target_nid), follow_redirects=True)
    
    def rename_node(self, nid, new_name):
        return self.client.post("/rename/%s" % nid, data=dict(name=new_name), follow_redirects=True)
    
    def vote(self, nid, undo=False, **kwargs):
        if not undo:
            return self.client.post("/vote/%s" % nid, follow_redirects=True, **kwargs)
        else:
            return self.client.post("/vote/%s?undo=true" % nid, follow_redirects=True, **kwargs)
    
    def delete_node(self, nid):
        return self.client.post("/delete/%s" % nid, follow_redirects=True)
    
    def restore_node(self, nid):
        return  self.client.post("/restore/%s" % nid, follow_redirects=True)
    
