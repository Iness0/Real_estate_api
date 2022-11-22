from flask import jsonify, Blueprint, abort, g, make_response
from flask_restful import Resource, Api, reqparse, fields, marshal, marshal_with, url_for
from models import models
from auth import auth
import json


customer_fields = {
    'id': fields.Integer,
    'email': fields.String,
    'number': fields.String,
    'houses': fields.List(fields.String)
}


def customer_or_404(customer_id):
    try:
        customer = models.Customer.query.get(customer_id)
    except ValueError:
        abort(404, "Customer does not exist.")
    else:
        return customer


class CustomerList(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email', required=True, help='Email address not provided',
                                   location=['json', 'form'])
        self.reqparse.add_argument('number', required=True, help='Mobile number not provided',
                                   location=['json', 'form'])
        self.reqparse.add_argument('password', required=True, help='Password not provided',
                                   location=['json', 'form'])
        self.reqparse.add_argument('house_id', required=False, location=['json', 'form'])
        super().__init__()

    @auth.login_required
    def get(self):
        customers = [marshal(customer, customer_fields) for customer in models.Customer.query.all()]
        return {'customers': customers}

    def post(self):
        args = self.reqparse.parse_args()
        new_user = models.Customer()
        new_user.create_customers(**args)
        print(new_user)
        return marshal(new_user, customer_fields), 201


class Customer(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email', required=False, store_missing=False,
                                   location=['form', 'json'])
        self.reqparse.add_argument('number', required=False, store_missing=False,
                                   location=['form', 'json'])
        self.reqparse.add_argument('password', required=False, store_missing=False,
                                   location=['form', 'json'])
        self.reqparse.add_argument('house_id', required=False, store_missing=False, location=['form', 'json'])

        super().__init__()

    @marshal_with(customer_fields)
    def get(self, id):
        return customer_or_404(id)

    @marshal_with(customer_fields)
    @auth.login_required
    def put(self, id):
        args = self.reqparse.parse_args()
        user = models.Customer.query.get(id)
        if user.email == g.user.email:
            user.update(**args)
            return user, 200, {'Location': url_for('customers.customer', id=id)}
        else:
            return make_response(json.dumps({'error': 'access denied'}), 401)

    @auth.login_required
    def delete(self, id):
        user = models.Customer.query.get(id)
        if user.email == g.user.email:
            user.delete()
            return '', 204, {'Location': url_for('customers.customers')}
        else:
            return make_response(json.dumps({'error': 'access denied'}), 401)


customers_api = Blueprint('customers', __name__)
api = Api(customers_api)
api.add_resource(CustomerList, '/api/customers', endpoint='customers')
api.add_resource(Customer, '/api/customers/<int:id>', endpoint='customer')
