from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from flask_restful_swagger_3 import Schema
from flask_restful_swagger_3 import Schema

from app.model.user import User

from app.core import db
#db = SQLAlchemy()
"""
+------------+---------+------+-----+---------+-------+
| Field      | Type    | Null | Key | Default | Extra |
+------------+---------+------+-----+---------+-------+
| uid        | int(11) | NO   | PRI | NULL    |       |
| friend_uid | int(11) | NO   | PRI | NULL    |       |
+------------+---------+------+-----+---------+-------+
"""
class Friendship(db.Model):
    __tablename__ = 'friendship'
    uid = db.Column(db.Integer, ForeignKey(User.uid), primary_key=True)
    friend_uid = db.Column(db.Integer, ForeignKey(User.uid), primary_key=True)