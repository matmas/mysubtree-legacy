#autoimport
from mysubtree.db import db


class Decrement(db.Model):
    node = db.Column(db.Integer(), primary_key=True)
    type = db.Column(db.String(255), primary_key=True)
    counter = db.Column(db.String(255), primary_key=True)
    at = db.Column(db.DateTime(), primary_key=True)
    amount = db.Column(db.Integer())
    