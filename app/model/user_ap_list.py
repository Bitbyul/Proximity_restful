from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_restful_swagger_3 import Schema

from app.model.user import User

from app.core import db
"""
+-----------+----------+------+-----+---------+----------------+
| Field     | Type     | Null | Key | Default | Extra          |
+-----------+----------+------+-----+---------+----------------+
| cid       | int(11)  | NO   | PRI | NULL    | auto_increment |
| uid       | int(11)  | NO   | MUL | NULL    |                |
| frequency | int(11)  | NO   |     | NULL    |                |
| bssid     | char(17) | NO   |     | NULL    |                |
| rssi      | int(11)  | NO   |     | NULL    |                |
+-----------+----------+------+-----+---------+----------------+
"""
class User_ap_list(db.Model):
    __tablename__ = 'user_ap_list'
    cid = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    uid = db.Column(db.Integer, ForeignKey(User.uid), nullable=False)
    frequency = db.Column(db.Integer, nullable=False)
    bssid = db.Column(db.String(17), nullable=False)
    rssi = db.Column(db.Integer, nullable=False)

class s_user_ap_list(Schema):
    type = 'object'
    properties = {
        'ap_list': {
            "type": "array",
            "properties": {
                'frequency': {"type": "integer"},
                'bssid': {"type": "string"},
                'rssi': {"type": "integer"},
            }
        }
    }
    required = ['ap_list']