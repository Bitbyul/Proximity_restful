from flask_sqlalchemy import SQLAlchemy
from flask_restful_swagger_3 import Schema

from app.core import db
#db = SQLAlchemy()
"""
+---------------+--------------+------+-----+---------+----------------+
| Field         | Type         | Null | Key | Default | Extra          |
+---------------+--------------+------+-----+---------+----------------+
| uid           | int(11)      | NO   | PRI | NULL    | auto_increment |
| id            | varchar(100) | NO   | UNI | NULL    |                |
| pw            | varchar(100) | NO   |     | NULL    |                |
| name          | varchar(100) | NO   |     | NULL    |                |
| email         | varchar(100) | YES  |     | NULL    |                |
| phone         | varchar(13)  | NO   |     | NULL    |                |
| photo         | varchar(100) | YES  |     | NULL    |                |
| search_permit | int(11)      | NO   |     | 1       |                |
+---------------+--------------+------+-----+---------+----------------+
"""
class User(db.Model):
    __tablename__ = 'users'
    
    uid = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    id = db.Column(db.String(100), nullable=False)
    pw = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(13))
    photo = db.Column(db.String(100))
    search_permit = db.Column(db.Integer, nullable=False)

class s_user_id_pw(Schema):
    type = 'object'
    properties = {
        'id': {"type": "string"},
        'pw': {"type": "string", 'format': 'password'}
    }
    required = ['id','pw']

class s_user_without_uid(Schema):
    type = 'object'
    properties = {
        'id': {"type": "string"},
        'pw': {"type": "string", 'format': 'password'},
        'name': {"type": "string"},
        'email': {"type": "string", 'format': 'email'},
        'phone': {"type": "string"},
        'photo': {"type": "string"},
    }
    required = ['id','pw','name','email','phone']
    
class s_user_only_id(Schema):
    type = 'object'
    properties = {
        'id': {"type": "string"}
    }
    required = ['id']
        
class s_user_only_uid(Schema):
    type = 'object'
    properties = {
        'uid': {"type": "integer"}
    }
    required = ['uid']