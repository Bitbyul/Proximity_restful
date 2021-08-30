from flask_restful_swagger_3 import Resource, Api, abort, swagger
from flask_restful import reqparse
from flask_jwt_extended import jwt_required
from flask_sqlalchemy import SQLAlchemy
import datetime
import json
from bson import json_util

from app.core import db
from app.model.user import *
from app.model.room import *
from app.model.user_in_room import *
from app.model.user_location import *
from app.model.friendship import *
from app.util import get_current_identity

@swagger.tags('Room')
class CreateRoom(Resource):
    decorators = [jwt_required(),]
    @swagger.security(**{"api_key": []})
    @swagger.response(response_code=200, description="정상 처리 완료")
    @swagger.parameters([{'in': 'query', 'name': 'body', 'description': '방 정보', 'schema': s_room_without_rid, 'required': 'true'}])
    def post(self):
        current_identity = get_current_identity()

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str)
        parser.add_argument('capacity', type=int)
        parser.add_argument('location_type', type=int)
        parser.add_argument('category_type', type=str)
        parser.add_argument('preferred_type', type=str)
        parser.add_argument('timeout_min', type=int)
        parser.add_argument('latitude', type=float)
        parser.add_argument('longitude', type=float)

        args = parser.parse_args()
        
        now = datetime.datetime.now() + datetime.timedelta(minutes=args['timeout_min'])
        dtstr = now.strftime('%Y-%m-%d %H:%M:%S')

        new_room = Room(
            name=args['name'],
            capacity=args['capacity'],
            location_type=args['location_type'],
            category_type=args['category_type'],
            preferred_type=args['preferred_type'],
            timeout_timestamp=dtstr,
            latitude=args['latitude'],
            longitude=args['longitude']
        )
        db.session.add(new_room)
        db.session.commit()

        moderator_in_room = User_in_room(
            uid=current_identity.uid,
            rid=new_room.rid,
            is_moderator=True
        )
        db.session.add(moderator_in_room)
        db.session.commit()

        return {
            'message': 'Successfully created.'
        }

@swagger.tags('Room')
class DeleteRoom(Resource):
    decorators = [jwt_required(),]
    @swagger.security(**{"api_key": []})
    @swagger.response(response_code=200, description="정상 처리 완료")
    @swagger.parameters([{'in': 'query', 'name': 'body', 'description': '방 RID', 'schema': s_room_only_rid, 'required': 'true'}])
    def post(self):
        current_identity = get_current_identity()

        parser = reqparse.RequestParser()
        parser.add_argument('rid', type=str)

        args = parser.parse_args()

        # 존재하는 방이거나 참여한 방인지 체크
        users_in_room = User_in_room.query.filter_by(uid=current_identity.uid, rid=args['rid'])
        if(users_in_room.count() == 0):
            return {
                'message': "can't find this room.",
            }, 403
        
        # 방장인지 체크
        if not (users_in_room.one().is_moderator):
            return {
                'message': "you aren't the moderator in this room.",
            }, 403

        # 방안에 있는 모든 인원 강퇴
        User_in_room.query.filter_by(rid=args['rid']).delete()
        
        # 방 삭제
        room = Room.query.filter_by(rid=args['rid']).one()
        db.session.delete(room)
        db.session.commit()
        
        return {
            'message': 'Successfully deleted.'
        }

@swagger.tags('Room')
class JoinRoom(Resource):
    decorators = [jwt_required(),]
    @swagger.security(**{"api_key": []})
    @swagger.response(response_code=200, description="정상 처리 완료")
    @swagger.parameters([{'in': 'query', 'name': 'body', 'description': '방 RID', 'schema': s_room_only_rid, 'required': 'true'}])
    def post(self):
        current_identity = get_current_identity()

        parser = reqparse.RequestParser()
        parser.add_argument('rid', type=str)

        args = parser.parse_args()

        # 이미 참여한 방인지 체크
        is_joined = User_in_room.query.filter_by(uid=current_identity.uid, rid=args['rid']).count()
        if(is_joined == 1):
            return {
                'message': "already joined in this room.",
            }, 403

        # 존재하는 방인지 체크
        is_room_exists = Room.query.filter_by(rid=args['rid']).count()
        if(is_room_exists == 0):
            return {
                'message': "can't find this room.",
            }, 403
            

        # 정원이 꽉 찼는지 체크
        users_in_room_count = User_in_room.query.filter_by(rid=args['rid']).count()
        room_capacity = Room.query.filter_by(rid=args['rid']).first().capacity
        if(users_in_room_count >= room_capacity):
            return {
                'message': "room is full.",
            }, 403

        user_in_room = User_in_room(
            uid=current_identity.uid,
            rid=args['rid'],
            is_moderator=False
        )
        db.session.add(user_in_room)
        db.session.commit()

        return {
            'message': 'Successfully joined.'
        }

@swagger.tags('Room')
class ExitRoom(Resource):
    decorators = [jwt_required(),]
    @swagger.security(**{"api_key": []})
    @swagger.response(response_code=200, description="정상 처리 완료")
    @swagger.parameters([{'in': 'query', 'name': 'body', 'description': '방 RID', 'schema': s_room_only_rid, 'required': 'true'}])
    def post(self):
        current_identity = get_current_identity()

        parser = reqparse.RequestParser()
        parser.add_argument('rid', type=str)

        args = parser.parse_args()

        # 존재하는 방인지 체크
        is_room_exists = Room.query.filter_by(rid=args['rid']).count()
        if(is_room_exists == 0):
            return {
                'message': "not joined in this room.",
            }, 403

        # 참여한 방인지 체크
        is_joined = User_in_room.query.filter_by(uid=current_identity.uid, rid=args['rid']).count()
        if(is_joined == 0):
            return {
                'message': "not joined in this room.",
            }, 403

        user_in_room = User_in_room.query.filter_by(uid=current_identity.uid, rid=args['rid']).one()

        # 방장이면 나가기 불가
        if(user_in_room.is_moderator):
            return {
                'message': "you're the moderator in this room.",
            }, 403

        db.session.delete(user_in_room)
        db.session.commit()

        return {
            'message': 'Successfully exited.'
        }

@swagger.tags('Room')
class KickUserInRoom(Resource):
    decorators = [jwt_required(),]
    @swagger.security(**{"api_key": []})
    @swagger.response(response_code=200, description="정상 처리 완료")
    @swagger.parameters([{'in': 'query', 'name': 'body', 'description': '방 RID, 타겟 유저 RID', 'schema': s_user_in_room, 'required': 'true'}])
    def post(self):
        current_identity = get_current_identity()

        parser = reqparse.RequestParser()
        parser.add_argument('rid', type=int)
        parser.add_argument('target_uid', type=int)

        args = parser.parse_args()

        # 참여한 방인지 체크
        is_joined = User_in_room.query.filter_by(uid=current_identity.uid, rid=args['rid']).count()
        if(is_joined == 0):
            return {
                'message': "you didn't join in this room.",
            }, 403

        # 방장인지 체크
        user_in_room = User_in_room.query.filter_by(uid=current_identity.uid, rid=args['rid']).one()
        if not (user_in_room.is_moderator):
            return {
                'message': "you aren't the moderator in this room.",
            }, 403
            
        # 나 자신인지 체크
        if current_identity.uid == args['target_uid']:
            return {
                'message': "you cannot kick yourself.",
            }, 403

        # 타겟이 존재하는지 체크
        target_in_room = User_in_room.query.filter_by(uid=args['target_uid'], rid=args['rid'])
        if(target_in_room.count() == 0):
            return {
                'message': "target didn't join in this room.",
            }, 403
            
        db.session.delete(target_in_room.one())
        db.session.commit()

        return {
            'message': 'Successfully kicked.'
        }

@swagger.tags('Room')
class ListRooms(Resource):
    decorators = [jwt_required(),]
    @swagger.security(**{"api_key": []})
    @swagger.response(response_code=200, description="정상 처리 완료")
    def get(self):
        """유저가 참여한 방 목록을 보여줍니다."""
        current_identity = get_current_identity()

        rooms_dict = []
        joined_rooms = User_in_room.query.filter_by(uid=current_identity.uid).all()

        for room in joined_rooms:
            room_info = Room.query.filter_by(rid=room.rid).one()
            room_info_dict = {
                'rid': room_info.rid,
                'name': room_info.name,
                'capacity': room_info.capacity,
                'location_type': room_info.location_type,
                'category_type': room_info.category_type,
                'preferred_type': room_info.preferred_type,
                'timeout_timestamp': str(room_info.timeout_timestamp),
                'latitude': room_info.latitude,
                'longitude': room_info.longitude
            }
            room_dict = {
                'rid': room.rid,
                'is_moderator': room.is_moderator,
                'joined_timestamp': str(room.joined_timestamp),
                'room_info': room_info_dict
            }
            rooms_dict.append(room_dict)

        return rooms_dict

@swagger.tags('Room')
class ListRoomUsers(Resource):
    decorators = [jwt_required(),]
    @swagger.security(**{"api_key": []})
    @swagger.response(response_code=200, description="정상 처리 완료")
    @swagger.parameters([{'in': 'query', 'name': 'body', 'description': '방 RID', 'schema': s_room_only_rid, 'required': 'true'}])
    def post(self):
        current_identity = get_current_identity()

        users_dict = []

        parser = reqparse.RequestParser()
        parser.add_argument('rid', type=int)
        
        args = parser.parse_args()

        is_joined = User_in_room.query.filter_by(uid=current_identity.uid, rid=args['rid']).count()
        if(is_joined == 0):
            return {
                'message': "user didn't join in this room.",
            }, 403
        joined_users = User_in_room.query.filter_by(rid=args['rid']).all()
        for user in joined_users:
            user_info = User.query.filter_by(uid=user.uid).one()
            location_info = User_location.query.filter_by(uid=user.uid).first()
            location_dict = {}

            if(location_info is None or user_info.search_permit < 1):
                location_dict = {
                    'latitude': 0,
                    'longitude': 0,
                    'accuracy': 0
                }
            else:
                location_dict = {
                    'latitude': location_info.latitude,
                    'longitude': location_info.longitude,
                    'accuracy': location_info.accuracy
                }

            user_info_dict = {
                'uid': user_info.uid,
                'id': user_info.id,
                'name': user_info.name,
                'email': user_info.email,
                'phone': user_info.phone,
                'photo': user_info.photo,
                'search_permit': user_info.search_permit
            }
            user_dict = {
                'uid': user.uid,
                'is_moderator': user.is_moderator,
                'user_info': user_info_dict,
                'location': location_dict
            }
            users_dict.append(user_dict)

        return users_dict

@swagger.tags('Room')
class ListNearbyRoom(Resource):
    decorators = [jwt_required(),]
    @swagger.security(**{"api_key": []})
    @swagger.response(response_code=200, description="정상 처리 완료")
    @swagger.parameters([{'in': 'query', 'name': 'body', 'description': '위도, 경도', 'schema': s_latlng, 'required': 'true'}])
    def post(self):
        current_identity = get_current_identity()

        rooms_dict = []

        parser = reqparse.RequestParser()
        parser.add_argument('latitude', type=str)
        parser.add_argument('longitude', type=str)
        
        args = parser.parse_args()

        result = db.engine.execute('SELECT * FROM ( SELECT *, ( 6371 * acos( cos( radians( '
                             + args['latitude'] + ' ) ) * cos( radians( latitude ) ) * cos( radians(  '
                             + args['longitude'] + ' ) - radians(127.128697) ) + sin( radians( '
                             + args['latitude'] + ' ) ) * sin( radians(latitude) ) ) ) AS distance FROM rooms ) DATA WHERE DATA.distance <= 5;')

        for r in result:
            r_dict = dict(r.items()) # convert to dict keyed by column names

            is_friend_joined = 0

            user_in_room = User_in_room.query.filter_by(rid=r_dict['rid'])
            now_user_count = user_in_room.count()

            my_friend_list = Friendship.query.filter_by(uid=current_identity.uid)

            # 친구가 있는 방인지 체크
            for room_user in user_in_room.all():
                for friend in my_friend_list.all():
                    if(room_user.uid == friend.friend_uid):
                        is_friend_joined = 1
                        break
                if(is_friend_joined==1):
                    break

            rooms_dict.append({
                'rid': r_dict['rid'],
                'now_user_count': now_user_count,
                'is_friend_joined':is_friend_joined,
                'name': r_dict['name'],
                'capacity': r_dict['capacity'],
                'location_type': r_dict['location_type'],
                'preferred_type': r_dict['preferred_type'],
                'category_type': r_dict['category_type'],
                'timeout_timestamp': str(r_dict['timeout_timestamp']),
                'latitude': float(r_dict['latitude']),
                'longitude': float(r_dict['longitude']),
                'distance': r_dict['distance']
                })

        return rooms_dict