from auth import basic_auth
from flask import jsonify, Blueprint, g
from flask_restful import Resource, Api


class Token(Resource):

    @basic_auth.login_required
    def get(self):
        token = g.user.generate_auth_token()
        token = token.decode('ascii')
        return jsonify({"token": token})


token_api = Blueprint('tokens', __name__)
api = Api(token_api)
api.add_resource(Token, '/api/tokens', endpoint='tokens')
# api.add_resource(House, '/api/houses/<int:id>', endpoint='house')