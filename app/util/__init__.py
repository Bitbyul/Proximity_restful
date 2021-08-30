from flask_jwt_extended import get_jwt_identity
import json

class UserIdentity:
    def __init__(self, **entries):
        self.__dict__.update(entries)

def get_current_identity():
    return UserIdentity(**json.loads(get_jwt_identity()))