from flask import jsonify, Blueprint, abort, url_for
from flask_restful import Resource, Api, reqparse, inputs, fields, marshal, marshal_with
from models import models
from resources.customers import customer_fields
from auth import auth


houses_fields = {
    'id': fields.Integer,
    'address': fields.String,
    'url': fields.String,
    'description': fields.String,
    'price': fields.String,
    'sold': fields.Boolean,
    'property_applicants': fields.List(fields.String)
}


def house_or_404(id):
    house = models.House.query.get(id)
    if house is not None:
        return house
    else:
        abort(404, "Wrong house id.")


class HouseList(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'address', required=True, help='No address provided',
            location=['form', 'json'])
        self.reqparse.add_argument(
            'url', required=False,
            location=['form', 'json'],
            type=inputs.url)
        self.reqparse.add_argument(
            'description', required=True, help='Please provide description',
            location=['form', 'json'])
        self.reqparse.add_argument(
            'price', required=True, help='No price provided',
            location=['form', 'json'])
        self.reqparse.add_argument(
            'sold', required=False, type=inputs.boolean, location=['form', 'json'])
        super().__init__()

    def get(self):
        houses = [marshal(house, houses_fields) for house in models.House.query.all()]
        return {'houses': houses}

    @marshal_with(houses_fields)
    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()
        new_house = models.House(**args)
        new_house.save_to_db()
        return new_house, 201, {'Location': url_for('houses.house', id=new_house.id)}


class House(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'address', required=False, help='No address provided',
            location=['form', 'json'])
        self.reqparse.add_argument(
            'url', required=False,
            location=['form', 'json'],
            type=inputs.url)
        self.reqparse.add_argument(
            'description', required=False,
            location=['form', 'json'])
        self.reqparse.add_argument(
            'price', required=False, type=inputs.positive, help='No price provided',
            location=['form', 'json'])
        self.reqparse.add_argument(
            'sold', required=False, type=inputs.boolean, location=['form', 'json'])
        super().__init__()

    @marshal_with(houses_fields)
    def get(self, id):
        return house_or_404(id)

    @marshal_with(houses_fields)
    @auth.login_required
    def put(self, id):
        args = self.reqparse.parse_args()
        house = models.House.query.get(id)
        house.update(**args)
        return house, 200, {'Location': url_for('houses.house', id=id)}

    @auth.login_required
    def delete(self, id):
        house = models.House.query.get(id)
        house.delete()
        return '', 204, {'Location': url_for('houses.houses')}


houses_api = Blueprint('houses', __name__)
api = Api(houses_api)
api.add_resource(HouseList, '/api/houses', endpoint='houses')
api.add_resource(House, '/api/houses/<int:id>', endpoint='house')
