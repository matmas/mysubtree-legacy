#autoimport
import uuid
import hashlib
import random
import string
from mysubtree.db import db

email_max_length = 254
username_max_length = 30
nickname_max_length = 15
_code_length = 10


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(email_max_length), unique=True)
    nick = db.Column(db.String(nickname_max_length))
    name = db.Column(db.String(username_max_length))
    hash = db.Column(db.String(64))  # (SHA256's hex length)
    salt = db.Column(db.String(36))  # (UUID's length)
    code = db.Column(db.String(_code_length), unique=True)
    date = db.Column(db.DateTime())
    node = db.Column(db.Integer(), unique=True)
    reset_code = db.Column(db.String(_code_length), unique=True)
    reset_date = db.Column(db.DateTime())
    num_problematic = db.Column(db.Integer(), default=0)
    num_unread_responses = db.Column(db.Integer(), default=0)
    
    def has_email_verified(self):
        return True if self.node else False
    
    def set_password(self, password):
        if not self.salt:
            self.salt = str(uuid.uuid4())
        self.hash = self._get_hash(password)
        assert self.has_password(password)
    
    def has_password(self, password):
        return self.hash == self._get_hash(password)
    
    def _get_hash(self, password):
        return hashlib.sha256((password + self.salt).encode("utf-8")).hexdigest()
    
    def generate_code(self):    #TODO what if duplicate reset_codes?
        length = _code_length
        return "".join(
            random.choice(string.letters + string.digits) for i in xrange(length)
        )
