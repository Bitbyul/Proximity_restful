from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from flask_restful_swagger_3 import Schema

from app.core import db
#db = SQLAlchemy()
"""
+--------------+------------+------+-----+---------+-------+
| Field        | Type       | Null | Key | Default | Extra |
+--------------+------------+------+-----+---------+-------+
| uid          | int(11)    | NO   | PRI | NULL    |       |
| rid          | int(11)    | NO   | PRI | NULL    |       |
| is_moderator | tinyint(1) | NO   |     | NULL    |       |
+--------------+------------+------+-----+---------+-------+
"""
class Room(db.Model):
    __tablename__ = 'rooms'
    
    rid = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    location_type = db.Column(db.Integer, nullable=False)
    category_type = db.Column(db.Integer, nullable=False)
    preferred_type = db.Column(db.Integer, nullable=False)
    timeout_timestamp = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None))
    longitude = db.Column(db.Numeric(precision=8, asdecimal=False, decimal_return_scale=None))

class s_room_without_rid(Schema):
    type = 'object'
    properties = {
        'name': {"type": "string", "description": "생성할 방의 이름"},
        'capacity': {"type": "integer"},
        'location_type': {"type": "integer", "enum":[0,1]},
        'category_type': {"type": "string"},
        'preferred_type': {"type": "string"},
        'timeout_min': {"type": "integer"},
        'latitude': {"type": "number", "format": "double"},
        'longitude': {"type": "number", "format": "double"}
    }
    required = ['name','capacity','location_type','category_type','timeout_min']

class s_room_only_rid(Schema):
    type = 'object'
    properties = {
        'rid': {"type": "integer"}
    }
    required = ['rid']

class s_latlng(Schema):
    type = 'object'
    properties = {
        'latitude': {"type": "number", "format": "double"},
        'longitude': {"type": "number", "format": "double"}
    }
    required = ['latitude','longitude']