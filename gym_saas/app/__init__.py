from flask import Flask
from .extensions import db, migrate, jwt
from gym_saas.config import DevelopmentConfig
from datetime import timedelta
from flask_jwt_extended import (verify_jwt_in_request, get_jwt_identity,
                                create_access_token, set_access_cookies)
from flask import make_response, request, redirect


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(DevelopmentConfig)
    app.config.from_pyfile("config.py", silent=True)

    # 🔐 JWT COOKIE CONFIG
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]

    app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"
    app.config["JWT_REFRESH_COOKIE_NAME"] = "refresh_token"

    app.config["JWT_ACCESS_COOKIE_PATH"] = "/"
    app.config["JWT_REFRESH_COOKIE_PATH"] = "/gym/refresh"

    app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    # 🔥 persistence
    app.config["JWT_SESSION_COOKIE"] = False

    # 🔥 expiry
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=1)

    # 🔥 Render-safe cookie flags
    app.config["JWT_COOKIE_SECURE"] = True
    app.config["JWT_COOKIE_SAMESITE"] = "None"

    # init extensions (ONLY once)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # ===============================
    # 🔁 AUTO REFRESH ACCESS TOKEN
    # ===============================
    @app.before_request
    def refresh_expiring_jwt():
        path = request.path

        # Skip static & auth routes
        if (
            path.startswith("/static") or
            path.startswith("/gym/login") or
            path.startswith("/gym/register") or
            path.startswith("/gym/refresh")
        ):
            return

        try:
            # If access token is valid → do nothing
            verify_jwt_in_request()
            return
        except Exception as e:
            # Only refresh if token is expired
            if "expired" not in str(e).lower():
                return

            try:
                verify_jwt_in_request(refresh=True)
                identity = get_jwt_identity()
                new_access = create_access_token(identity=identity)

                resp = make_response()
                set_access_cookies(resp, new_access)
                return resp
            except Exception:
                pass

    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        return {"msg": "missing or invalid token"}, 401

    @jwt.expired_token_loader
    def expired_callback(jwt_header, jwt_payload):
        return redirect("/")

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return {"msg": "invalid token"}, 401

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
