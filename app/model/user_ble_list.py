from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_restful_swagger_3 import Schema

from app.model.user import User

from app.core import db
"""
+-------+----------+------+-----+---------+----------------+
| Field | Type     | Null | Key | Default | Extra          |
+-------+----------+------+-----+---------+----------------+
| cid   | int(11)  | NO   | PRI | NULL    | auto_increment |
| uid   | int(11)  | NO   | MUL | NULL    |                |
| bssid | char(17) | NO   |     | NULL    |                |
| rssi  | int(11)  | NO   |     | NULL    |                |
+-------+----------+------+-----+---------+----------------+
"""
class User_ble_list(db.Model):
    __tablename__ = 'user_ble_list'
    cid = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    uid = db.Column(db.Integer, ForeignKey(User.uid), nullable=False)
    address = db.Column(db.String(17), nullable=False)
    rssi = db.Column(db.Integer, nullable=False)