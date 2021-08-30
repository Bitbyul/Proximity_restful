from flask_restful_swagger_3 import Resource, Api, abort, swagger
from flask_restful import reqparse
#from flask_jwt import JWT, jwt_required, current_identity, _jwt, JWTError
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import safe_str_cmp
import requests, json
import threading
from json import JSONEncoder

from app.core import db
from app.model.user import *
from app.model.user_in_room import *
from app.model.friendship import *
from app.model.user_location import *
from app.model.user_ap_list import *
from app.model.user_ble_list import *
from app.util import get_current_identity

# subclass JSONEncoder
class UserEncoder(JSONEncoder):
        def default(self, o):
            return {
                'uid': o.uid,
                'id': o.id,
                'pw': o.pw,
                'name': o.name,
                'email': o.email,
                'phone': o.phone,
                'photo': o.photo,
                'search_permit': o.search_permit,
            }

@swagger.tags('User')
class CreateUser(Resource):
    @swagger.response(response_code=200, description="정상적으로 등록되었습니다.")
    @swagger.parameters([{'in': 'query', 'name': 'body', 'description': '유저 정보', 'schema': s_user_without_uid, 'required': 'true'}])
    def post(self):
        """회원가입합니다."""
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str)
        parser.add_argument('pw', type=str)
        parser.add_argument('name', type=str)
        parser.add_argument('email', type=str)
        parser.add_argument('phone', type=str)
        parser.add_argument('photo', type=str)
        args = parser.parse_args()

        new_user = User(
            id=args['id'],
            pw=args['pw'],
            name=args['name'],
            email=args['email'],
            phone=args['phone'],
            photo=args['photo'],
            search_permit=1 # default
        )
        db.session.add(new_user)
        db.session.commit()

        return {
            'status_code': 200,
            'created_uid': new_user.uid,
            'message': 'Successfully registered.'
        }

@swagger.tags('User')
class CheckID(Resource):
    @swagger.response(response_code=200, description="is_duplicated가 1이면 중복 존재, 0이면 생성 가능")
    @swagger.parameters([{'in': 'query', 'name': 'body', 'description': '유저 ID', 'schema': s_user_only_id, 'required': 'true'}])
    def post(self):
        """ID가 생성 가능한지 검증합니다."""
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str)
        args = parser.parse_args()
        user = User.query.filter_by(id=args['id'])

        if(user.count() > 0):
            return {
                'is_duplicated': 1,
            }, 200
            
        return {
            'is_duplicated': 0,
        }, 200

@swagger.tags('User')
class DeleteUser(Resource):
    decorators = [jwt_required(),]
    @swagger.security(**{"api_key": []})
    @swagger.response(response_code=200, description="삭제 완료")
    @swagger.response(response_code=401, description="로그인되지 않았습니다. 혹은 토큰 만료.")
    def get(self):
        """현재 로그인된 유저를 회원탈퇴(삭제) 처리합니다."""
        current_identity = get_current_identity()

        # 참여한 방이 있는지 체크
        users_in_room = User_in_room.query.filter_by(uid=current_identity.uid)
        if(users_in_room.count() > 0):
            return {
                'message': 'You are participating in the room.'
            }

        # 친구관계 제거
        friendship = Friendship.query.filter_by(uid=current_identity.uid).delete()
        friendship = Friendship.query.filter_by(friend_uid=current_identity.uid).delete()

        # 위치정보 제거
        User_location.query.filter_by(uid=current_identity.uid).delete()
        User_ap_list.query.filter_by(uid=current_identity.uid).delete()
        User_ble_list.query.filter_by(uid=current_identity.uid).delete()

        # 유저 제거
        user = User.query.filter_by(uid=current_identity.uid).one()
        db.session.delete(user)
        db.session.commit()


        return {
            'message': 'Unregistered successfully. Goodbye.'
        }

@swagger.tags('User')
class FetchUser(Resource):
    decorators = [jwt_required(),]
    @swagger.security(**{"api_key": []})
    @swagger.response(response_code=200, description="정상 처리 완료")
    def get(self):
        """현재 로그인된 유저 정보를 불러옵니다."""
        current_identity = get_current_identity()
        
        user = User.query.filter_by(uid=current_identity.uid).one()

        return {
            'status_code': 200,
            'user': {
                'uid': user.uid,
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'photo': user.photo,
                'search_permit': user.search_permit
                }
            }

@swagger.tags('User')
class ModifySearchPermit(Resource):
    decorators = [jwt_required(),]
    def post(self):
        current_identity = get_current_identity()

        parser = reqparse.RequestParser()
        parser.add_argument('search_permit', type=int)
        args = parser.parse_args()

        user = User.query.filter_by(uid=current_identity.uid).first()
        if not user:
            return {'message': 'cannot find the user.'}, 404
        
        user.search_permit = args['search_permit']
        db.session.commit()

        return {'message': 'successfully updated.'}


@swagger.tags('User')
class AuthUser_legacy(Resource):
    def post(self):
        """유저의 아이디와 비밀번호로 토큰을 발급받습니다 (Legacy for flask_jwt)."""

        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str)
        parser.add_argument('pw', type=str)
        args = parser.parse_args()

        data = {'id': args['id'], 'pw': args['pw']}

        criterion = [args['id'], args['pw']]

        if not all(criterion):
            raise JWTError('Bad Request', 'Invalid credentials')

        identity = _jwt.authentication_callback(args['id'], args['pw'])

        if identity:
            access_token = _jwt.jwt_encode_callback(identity)
            return _jwt.auth_response_callback(access_token, identity)
        else:
            raise JWTError('Bad Request', 'Invalid credentials')

@swagger.tags('User')
class AuthUser(Resource):
    @swagger.response(response_code=200, description="인증 완료")
    @swagger.response(response_code=401, description="인증 실패")
    @swagger.parameters([{'in': 'query', 'name': 'body', 'description': '유저 ID, PW', 'schema': s_user_id_pw, 'required': 'true'}])
    def post(self):
        """유저의 아이디와 비밀번호로 토큰을 발급받습니다."""
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str)
        parser.add_argument('pw', type=str)
        args = parser.parse_args()

        user = User.query.filter_by(id=args['id']).first()
        
        if user and safe_str_cmp(user.pw.encode('utf-8'), args['pw'].encode('utf-8')):
            access_token = create_access_token(identity=UserEncoder().encode(user))
            refresh_token = create_refresh_token(identity=UserEncoder().encode(user))
            return {"access_token": access_token, "refresh_token": refresh_token} # zzzz
        else:
            return {"message": "Bad username or password"}, 401

@swagger.tags('User')
class RefreshUser(Resource):
    decorators = [jwt_required(refresh=True),]
    @swagger.security(**{"api_key": []})
    @swagger.response(response_code=200, description="정상 처리 완료")
    def get(self):
        """유저의 토큰을 갱신합니다."""
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return {"access_token": access_token}

        
@swagger.tags('User')
class FetchFriends(Resource):
    decorators = [jwt_required(),]
    @swagger.security(**{"api_key": []})
    @swagger.response(response_code=200, description="정상 처리 완료")
    def get(self):
        """친구 목록을 불러옵니다."""
        users_dict = []

        current_identity = get_current_identity()

        friends = db.session.query(User, Friendship).filter(Friendship.uid==current_identity.uid).filter(User.uid==Friendship.friend_uid).all()

        for user, friends in friends:

            location_info = User_location.query.filter_by(uid=user.uid).first()
            ap_list = User_ap_list.query.filter_by(uid=user.uid).all()
            ble_list = User_ble_list.query.filter_by(uid=user.uid).all()
            aps_dict = []
            bles_dict = []

            for ap in ap_list:
                ap_dict = {
                    'frequency': ap.frequency,
                    'bssid': ap.bssid,
                    'rssi': ap.rssi
                }
                aps_dict.append(ap_dict)

            for ble in ble_list:
                ble_dict = {
                    'address': ble.address,
                    'rssi': ble.rssi
                }
                bles_dict.append(ble_dict)

            location_dict = {}

            if((not location_info) or (user.search_permit < 1)):
                location_dict = {
                    'latitude': 0,
                    'longitude': 0,
                    'accuracy': 0
                }
            else:
                location_dict = {
                    'latitude': location_info.latitude,
                    'longitude': location_info.longitude,
                    'accuracy': location_info.accuracy,
                    'nearby_wifi_info_list': aps_dict,
                    'nearby_ble_info_list': bles_dict
                }

            user_info_dict = {
                'uid': user.uid,
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'photo': user.photo,
                'search_permit': user.search_permit
            }

            user_dict = {
                'uid': user.uid,
                'user_info': user_info_dict,
                'location': location_dict
            }
            users_dict.append(user_dict)

        return users_dict

@swagger.tags('User')
class AddFriend(Resource):
    decorators = [jwt_required(),]
    @swagger.security(**{"api_key": []})
    @swagger.response(response_code=200, description="정상 처리 완료")
    @swagger.parameters([{'in': 'query', 'name': 'body', 'description': '유저 ID', 'schema': s_user_only_id, 'required': 'true'}])
    def post(self):
        current_identity = get_current_identity()

        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str)
        args = parser.parse_args()

        if(current_identity.id == args['id']):
            return {"message": "cannot add yourself as a friend."}

        user = User.query.filter_by(id=args['id']).first()

        if not user:
            return {"message": "user not found."}
        
        friendship = Friendship.query.filter_by(uid=current_identity.uid, friend_uid=user.uid).first()

        if friendship:
            return {"message": "user is already a friend."}

        new_friendship = Friendship(
            uid=current_identity.uid,
            friend_uid=user.uid
        )
        db.session.add(new_friendship)
        db.session.commit()

        return {"message": "successfully registered."}
        
@swagger.tags('User')
class DeleteFriend(Resource):
    decorators = [jwt_required(),]
    @swagger.security(**{"api_key": []})
    @swagger.response(response_code=200, description="정상 처리 완료")
    @swagger.parameters([{'in': 'query', 'name': 'body', 'description': '유저 ID', 'schema': s_user_only_uid, 'required': 'true'}])
    def post(self):
        current_identity = get_current_identity()

        parser = reqparse.RequestParser()
        parser.add_argument('uid', type=int)
        args = parser.parse_args()
        
        friendship = Friendship.query.filter_by(uid=current_identity.uid, friend_uid=args['uid']).first()

        if not friendship:
            return {"message": "user is not a friend."}

        db.session.delete(friendship)
        db.session.commit()

        return {"message": "successfully unregistered."}
                
@swagger.tags('User')
class SearchByID(Resource):
    decorators = [jwt_required(),]
    @swagger.security(**{"api_key": []})
    @swagger.response(response_code=200, description="정상 처리 완료")
    @swagger.parameters([{'in': 'query', 'name': 'body', 'description': '유저 ID', 'schema': s_user_only_id, 'required': 'true'}])
    def post(self):
        current_identity = get_current_identity()

        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str)
        args = parser.parse_args()
        
        user = User.query.filter_by(id=args['id']).first()

        if not user:
            return {"message": "user not found."}, 404

        user_info_dict = {
            'uid': user.uid,
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'photo': user.photo,
        }
        user_dict = {
            'uid': user.uid,
            'user_info': user_info_dict
        }

        return user_dict
        
@swagger.tags('User')
class PutLocation(Resource):
    decorators = [jwt_required(),]
    @swagger.security(**{"api_key": []})
    @swagger.response(response_code=200, description="정상 처리 완료")
    @swagger.parameters([{'in': 'query', 'name': 'body', 'description': '유저 ID', 'schema': s_user_location, 'required': 'true'}])
    def post(self):
        current_identity = get_current_identity()

        parser = reqparse.RequestParser()
        parser.add_argument('latitude', type=float)
        parser.add_argument('longitude', type=float)
        parser.add_argument('accuracy', type=float)
        args = parser.parse_args()

        print("lat: "+str(args['latitude'])+", lng: "+str(args['longitude'])+", accu: "+str(args['accuracy']))

        user_location = User_location.query.filter_by(uid=current_identity.uid).delete()
        db.session.commit()

        new_user_location = User_location(
            uid=current_identity.uid, 
            latitude=args['latitude'], 
            longitude=args['longitude'], 
            accuracy=args['accuracy']
            )

        db.session.add(new_user_location)
        db.session.commit()

        return {"message": "OK"}

@swagger.tags('User')
class GetLocation(Resource):
    decorators = [jwt_required(),]
    @swagger.security(**{"api_key": []})
    @swagger.response(response_code=200, description="정상 처리 완료")
    @swagger.parameters([{'in': 'query', 'name': 'body', 'description': '유저 ID', 'schema': s_user_only_uid, 'required': 'true'}])
    def post(self):
        current_identity = get_current_identity()

        parser = reqparse.RequestParser()
        parser.add_argument('uid', type=int)
        args = parser.parse_args()

        user_location = User_location.query.filter_by(uid=args['uid']).one()

        return {
            'latitude': user_location.latitude,
            'longitude': user_location.longitude,
            'accuracy': user_location.accuracy
        }

@swagger.tags('User')
class PutAPList(Resource):
    decorators = [jwt_required(),]
    @swagger.security(**{"api_key": []})
    @swagger.response(response_code=200, description="정상 처리 완료")
    @swagger.parameters([{'in': 'query', 'name': 'body', 'description': '유저 ID', 'schema': s_user_ap_list, 'required': 'true'}])
    def post(self):
        current_identity = get_current_identity()

        parser = reqparse.RequestParser()
        parser.add_argument('ap_list', type=dict,action="append")
        args = parser.parse_args()

        if not (args['ap_list'] is None):
            User_ap_list.query.filter_by(uid=current_identity.uid).delete()
            for ap in args['ap_list']:
                new_user_ap = User_ap_list(
                    uid=current_identity.uid,
                    frequency=ap['frequency'],
                    bssid=ap['bssid'],
                    rssi=ap['rssi'],
                )
                db.session.add(new_user_ap)
            db.session.commit()

        return {"message": "OK"}

@swagger.tags('User')
class PutBLEList(Resource):
    decorators = [jwt_required(),]
    @swagger.security(**{"api_key": []})
    @swagger.response(response_code=200, description="정상 처리 완료")
    def post(self):
        current_identity = get_current_identity()

        parser = reqparse.RequestParser()
        parser.add_argument('ble_list', type=dict,action="append")
        args = parser.parse_args()

        if not (args['ble_list'] is None):
            User_ble_list.query.filter_by(uid=current_identity.uid).delete()
            for ble in args['ble_list']:
                new_user_ble = User_ble_list(
                    uid=current_identity.uid,
                    address=ble['address'],
                    rssi=ble['rssi'],
                )
                db.session.add(new_user_ble)
            db.session.commit()

        return {"message": "OK"}
