from flask import Flask
from .extensions import db, migrate, jwt
from config import DevelopmentConfig

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(DevelopmentConfig)
    app.config.from_pyfile("config.py", silent=True)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app import models
    from app.routes import api_v1
    app.register_blueprint(api_v1)

    return app

