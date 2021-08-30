import types
from datetime import timedelta

#from flask_restful import Resource, Api, abort
#from flask_jwt import JWT, jwt_required, current_identity
from flask_jwt_extended import JWTManager

from app.model.user import User
from . import user, room

"""
def authenticate(id, pw):
    user = User.query.filter_by(id=id).first()
    if user and safe_str_cmp(user.pw.encode('utf-8'), pw.encode('utf-8')):
        return user

def identity(payload):
    user_id = payload['identity']
    return User.query.filter_by(id=user_id).first() #.get(user_id)

def checkuser(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        #if current_identity.id == 'test1':
        return func(*args, **kwargs)
        #return abort(401)
    return wrapper
"""

def register_resources(app, api):
    # JWT 설정
    """
    app.config["JWT_AUTH_USERNAME_KEY"] = "id"
    app.config["JWT_AUTH_PASSWORD_KEY"] = "pw"
    app.config["JWT_AUTH_HEADER_PREFIX"] = "Bearer"
    app.config['PROPAGATE_EXCEPTIONS'] = True
    
    jwt = JWT(app, authenticate, identity) # flask_JWT
    """
    # flask_JWT_extended
    app.config["JWT_SECRET_KEY"] = "%qw#GHD*f23QG5$"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

    jwt = JWTManager(app)
    
    api.add_resource(user.AuthUser, '/user/auth')
    api.add_resource(user.RefreshUser, '/user/refresh')
    api.add_resource(user.FetchUser, '/user/fetch')
    api.add_resource(user.ModifySearchPermit, '/user/modifysearchpermit')
    api.add_resource(user.CheckID, '/user/checkid')
    api.add_resource(user.CreateUser, '/user/register')
    api.add_resource(user.DeleteUser, '/user/unregister')
    api.add_resource(user.FetchFriends, '/user/fetchfriends')
    api.add_resource(user.AddFriend, '/user/addfriend')
    api.add_resource(user.DeleteFriend, '/user/deletefriend')
    api.add_resource(user.SearchByID, '/user/searchbyid')
    api.add_resource(user.PutLocation, '/user/putlocation')
    api.add_resource(user.GetLocation, '/user/getlocation')
    api.add_resource(user.PutAPList, '/user/putaplist')
    api.add_resource(user.PutBLEList, '/user/putblelist')

    api.add_resource(room.CreateRoom, '/room/create')
    api.add_resource(room.DeleteRoom, '/room/delete')
    api.add_resource(room.JoinRoom, '/room/join')
    api.add_resource(room.ExitRoom, '/room/exit')
    api.add_resource(room.KickUserInRoom, '/room/kickuser')
    api.add_resource(room.ListRooms, '/room/list')
    api.add_resource(room.ListRoomUsers, '/room/listuser')
    api.add_resource(room.ListNearbyRoom, '/room/listnearby')