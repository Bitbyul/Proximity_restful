from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_restful_swagger_3 import Schema

from app.model.user import User

from app.core import db
"""
+-----------+----------------+------+-----+---------+-------+
| Field     | Type           | Null | Key | Default | Extra |
+-----------+----------------+------+-----+---------+-------+
| uid       | int(11)        | NO   | PRI | NULL    |       |
| latitude  | decimal(18,10) | YES  |     | NULL    |       |
| longitude | decimal(18,10) | YES  |     | NULL    |       |
| accuracy  | decimal(18,10) | YES  |     | NULL    |       |
+-----------+----------------+------+-----+---------+-------+
"""

class User_location(db.Model):
    __tablename__ = 'user_location'
    uid = db.Column(db.Integer, ForeignKey(User.uid), primary_key=True)
    latitude = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None))
    longitude = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None))
    accuracy = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None))

class s_user_location(Schema):
    type = 'object'
    properties = {
        'latitude': {"type": "number", "format": "double"},
        'longitude': {"type": "number", "format": "double"},
        'accuracy': {"type": "number", "format": "float"}
    }
    required = ['rid']