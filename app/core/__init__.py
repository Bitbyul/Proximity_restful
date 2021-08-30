from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful_swagger_3 import Resource, Api, abort, get_swagger_blueprint

app = Flask(__name__) # flask instance
app.secret_key = 'Z%RhG_Z*PZn$'

app.config['JSON_AS_ASCII'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True

# database 설정
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://proximity_api:####@localhost:3306/proximity"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Swagger 설정
authorizations = {
    "api_key": {
        "type": "http",
        "in": "header",
        "name": "Authorization",
        "scheme": "bearer"
    }
}

# flask_sqlalchemy
db = SQLAlchemy(app)

# flask_restful + swagger_3
api = Api(app, version='0.0', title='Proximity App API Documentation', authorizations=authorizations)
swagger_blueprint = get_swagger_blueprint(api.open_api_object)

from app.api.v1 import register_resources
register_resources(app, api)

app.register_blueprint(swagger_blueprint)



"""
class Username(Resource):
    @swag_from('username_specs.yml', methods=['GET'])
    def get(self, username):
        return {'username': username}, 200

api.add_resource(Username, '/username/<username>')
"""