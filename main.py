from flask import Flask, g, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import DevelopmentConfig as Config
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address, default_limits=[Config.DEFAULT_RATE])


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config())

    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    from resources.houses import houses_api
    app.register_blueprint(houses_api)
    from resources.customers import customers_api
    app.register_blueprint(customers_api)
    from resources.token import token_api
    app.register_blueprint(token_api)

    limiter.limit("30/day", per_method=True, methods=["POST", "DELETE"])(customers_api)
    limiter.limit(Config.DEFAULT_RATE, per_method=True, methods=["GET", "POST", "DELETE"])(houses_api)

    return app


from models import models
