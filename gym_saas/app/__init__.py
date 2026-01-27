from flask import Flask
from .extensions import db, migrate, jwt
from gym_saas.config import DevelopmentConfig

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(DevelopmentConfig)
    app.config.from_pyfile("config.py", silent=True)

    # 🔐 JWT COOKIE CONFIG (CRITICAL)
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_ACCESS_COOKIE_PATH"] = "/"
    app.config["JWT_REFRESH_COOKIE_PATH"] = "/"
    app.config["JWT_COOKIE_SECURE"] = False      # REQUIRED for Replit
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from . import models
    from .routes import api_v1
    app.register_blueprint(api_v1)

    return app

