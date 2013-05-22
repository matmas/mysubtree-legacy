#autoimport
from flask import request
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.event import listen
from lib.autoimport import autoimport_modules
from lib.base57 import base_decode
from mysubtree.web.app import app

db = SQLAlchemy(app, session_options={"expire_on_commit": False})

#=== <model>.after_attach() ====================================================
def _after_attach(session, instance):
    after_attach_hook = getattr(instance, "after_attach", None)
    if callable(after_attach_hook):
        after_attach_hook()
listen(db.session.__class__, "after_attach", _after_attach)
#=== <model>.before_commit() ====================================================
def _before_commit(session):
    session._commited_instances = session.dirty
listen(db.session.__class__, "before_commit", _before_commit)
#=== <model>.after_commit() ====================================================
def _after_commit(session):
    for instance in session._commited_instances:
        after_commit_hook = getattr(instance, "after_commit", None)
        if callable(after_commit_hook):
            after_commit_hook()
    del session._commited_instances
listen(db.session.__class__, "after_commit", _after_commit)

#===============================================================================

def autoimport_and_init_db():
    for module in autoimport_modules(__file__, __package__):
        __import__(module)
    db.create_all()
    _ensure_initial_data()
    
def _ensure_initial_data():
    from mysubtree.backend import backend
    from mysubtree.backend.models.node.types.all import get_model
    from mysubtree.backend.models.node.types.users import Users
    from mysubtree.backend.models.node.node import Node
    from mysubtree.backend.models.user import User
    
    if not backend.get_node(_basic_nodes[0]["id"]):
        created_nodes = {}
        for basic_node in _basic_nodes:
            node = get_model(basic_node["type"])()
            node.lang = basic_node["lang"]
            node.id = basic_node["id"]
            created_nodes[node.id] = node
            if basic_node["parent"]:
                node.set_parent(created_nodes[basic_node["parent"]])
            else:
                node.set_parent(None)
            db.session.add(node)
            node.increment_counters()
            db.session.flush()
        
        # create first user
        user = User()
        user.email = "riesz.martin@gmail.com"
        user.name = "Matmas"
        user.set_password("CommonPassword")
        db.session.add(user)
        
        usernode = Users(username=user.name)
        db.session.add(usernode)
        user.node = usernode.id
        
        db.session.commit()

_en_root_id = base_decode("en")
_sk_root_id = base_decode("sk")

_basic_nodes = [
    {"id": _en_root_id, "type": "root",  "lang": "en", "parent": None},
    {"id": 2, "type": "trash", "lang": "en", "parent": _en_root_id},
    {"id": _sk_root_id, "type": "root",  "lang": "sk", "parent": None},
    {"id": 4, "type": "trash", "lang": "sk", "parent": _sk_root_id},
]

#def get_lang():
    #return app.config["LANGUAGES"][request.host.split(":")[0]]

def get_root_id(lang):
    return base_decode(lang)
    #return [node for node in _basic_nodes if node["lang"] == lang and node["type"] == "root"][0]["id"]

def get_trash_id(lang):
    return [node for node in _basic_nodes if node["lang"] == lang and node["type"] == "trash"][0]["id"]

#def _get_languages():
    #return [node["lang"] for node in _basic_nodes if node["type"] == "root"]
