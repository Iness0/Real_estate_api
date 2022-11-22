import datetime
from flask import make_response, abort
from sqlalchemy.orm import relationship
from main import db
from argon2 import PasswordHasher
from datetime import datetime, timedelta
from authlib.jose import jwt, JsonWebKey
from authlib.jose.errors import ExpiredTokenError
import base64
import os
import json

hasher = PasswordHasher()

association_table = db.Table('wants_to_buy',
                             db.Column('house_id', db.ForeignKey('houses.id'), primary_key=True),
                             db.Column('customers_id', db.ForeignKey('customers.id'), primary_key=True))


class House(db.Model):
    __tablename__ = 'houses'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(128), unique=True, nullable=False)
    url = db.Column(db.String(128), unique=True)
    description = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    price = db.Column(db.Integer)
    sold = db.Column(db.Boolean, default=False)
    property_applicants = relationship('Customer', secondary=association_table, back_populates="houses", lazy='dynamic')

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True)
    number = db.Column(db.String(32), unique=True)
    password_hash = db.Column(db.String(128))
    active = db.Column(db.Boolean, default=True)
    houses = relationship('House', secondary=association_table, back_populates='property_applicants', lazy='dynamic')


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'house_id':
                house = House.query.get(value)
                self.follow_house(house)
            elif key == 'password':
                raise Exception('Password can not be changed')
            else:
                setattr(self, key, value)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def follow_house(self, house):
        self.houses.append(house)

    @classmethod
    def create_customers(cls, email, number, password, house_id):
        email = email.lower()
        existing = cls.query.filter((cls.email == email) | (cls.number == number)).first()
        if existing is not None:
            raise Exception('Please use different email or number')
        customer = cls(email=email, number=number)
        customer.password_hash = customer.set_password(password)
        if house_id is not None:
            house = House.query.get(house_id)
            customer.follow_house(house)
        db.session.add(customer)
        db.session.commit()
        return customer

    @staticmethod
    def set_password(password):
        return hasher.hash(password)

    def verify_password(self, password):
        return hasher.verify(self.password_hash, password)

    @staticmethod
    def validate_token(token):
        with open('public.pem', 'r') as data:
            jwk = data.read()
        claims = jwt.decode(token, jwk)
        try:
            claims.validate()
        except ExpiredTokenError:
            abort(401, "token has expired")
        return Customer.query.get(claims['sub'])

    def generate_auth_token(self, expires_in=3600):
        with open('private.pem', 'r') as data:
            jwk = json.load(data)
            print(jwk)

        header = {'alg': 'ES256'}
        payload = {
            'iss': 'real_estate',
            'aud': 'api_auth',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'sub': self.id
        }
        token = jwt.encode(header, payload, jwk)
        return token
