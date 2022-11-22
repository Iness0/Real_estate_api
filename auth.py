from flask import g
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from models.models import Customer


basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth(scheme='Token')
auth = MultiAuth(token_auth, basic_auth)


@basic_auth.verify_password
def verify_password(username, password):
    user = Customer.query.filter_by(email=username).first()
    if user is not None and user.verify_password(password):
        g.user = user
        return True
    else:
        return False


@token_auth.verify_token
def verify_token(token):
    user = Customer.validate_token(token)
    if user is not None:
        g.user = user
        return True
    return False

