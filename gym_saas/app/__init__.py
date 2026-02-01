from flask import Flask
from .extensions import db, migrate, jwt
from gym_saas.config import DevelopmentConfig
from flask import redirect, url_for
from datetime import timedelta

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(DevelopmentConfig)
    app.config.from_pyfile("config.py", silent=True)

    # 🔐 JWT COOKIE CONFIG
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]

    app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"
    app.config["JWT_REFRESH_COOKIE_NAME"] = "refresh_token"

    app.config["JWT_ACCESS_COOKIE_PATH"] = "/"
    app.config["JWT_REFRESH_COOKIE_PATH"] = "/"

    app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    # 🔥 persistence
    app.config["JWT_SESSION_COOKIE"] = False

    # 🔥 expiry
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

    # 🔥 Render-safe cookie flags
    if not app.debug:
        app.config["JWT_COOKIE_SECURE"] = True
        app.config["JWT_COOKIE_SAMESITE"] = "None"
    else:
        app.config["JWT_COOKIE_SECURE"] = False
        app.config["JWT_COOKIE_SAMESITE"] = "Lax"


    # init extensions (ONLY once)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        return redirect(url_for("api_v1.gym_auth.login_page"))

    @jwt.expired_token_loader
    def expired_callback(jwt_header, jwt_payload):
        return redirect(url_for("api_v1.gym_auth.login_page"))

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return redirect(url_for("api_v1.gym_auth.login_page"))
        
    # import AFTER init
    from . import models
    from .routes import api_v1
    app.register_blueprint(api_v1)
    from gym_saas.app.routes.public import public_bp
    app.register_blueprint(public_bp)

    # create tables (MVP only)
    with app.app_context():
        db.create_all()

    return app
