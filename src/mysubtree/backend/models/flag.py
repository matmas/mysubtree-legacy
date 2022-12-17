from mysubtree.db import db


class Flag(db.Model):
    node = db.Column(db.Integer(), primary_key=True)
    ip = db.Column(db.String(255), primary_key=True)
    