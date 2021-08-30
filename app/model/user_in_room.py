from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_restful_swagger_3 import Schema

from app.model.user import User
from app.model.room import Room

from app.core import db
#db = SQLAlchemy()
"""
+------------------+------------+------+-----+-------------------+-------+
| Field            | Type       | Null | Key | Default           | Extra |
+------------------+------------+------+-----+-------------------+-------+
| uid              | int(11)    | NO   | PRI | NULL              |       |
| rid              | int(11)    | NO   | PRI | NULL              |       |
| is_moderator     | tinyint(1) | NO   |     | NULL              |       |
| joined_timestamp | datetime   | NO   |     | CURRENT_TIMESTAMP |       |
+------------------+------------+------+-----+-------------------+-------+
"""
class User_in_room(db.Model):
    __tablename__ = 'users_in_room'
    uid = db.Column(db.Integer, ForeignKey(User.uid), primary_key=True)
    rid = db.Column(db.Integer, ForeignKey(Room.rid), primary_key=True)
    joined_timestamp = db.Column(db.DateTime, nullable=False)
    is_moderator = db.Column(db.Boolean, nullable=False)

class s_user_in_room(Schema):
    type = 'object'
    properties = {
        'uid': {"type": "integer"},
        'rid': {"type": "integer"}
    }
    required = ['rid']