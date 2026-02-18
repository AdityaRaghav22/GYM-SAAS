from flask import Flask
from .extensions import db, migrate, jwt
from gym_saas.config import DevelopmentConfig
from datetime import timedelta
from flask import request, redirect, url_for, flash

def is_browser():
    return "text/html" in request.headers.get("Accept", "")

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(DevelopmentConfig)
    app.config.from_pyfile("config.py", silent=True)

    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

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

    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        if is_browser():
            flash("Please login to continue.", "warning")
            return redirect(url_for("gym_auth.login_page"))
        return {"msg": "missing or invalid token"}, 401

    @jwt.expired_token_loader
    def expired_callback(jwt_header, jwt_payload):
        if is_browser():
            flash("Session expired. Please login again.", "error")
            return redirect(url_for("gym_auth.login_page"))
        return {"msg": "token expired"}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        if is_browser():
            flash("Invalid session. Please login again.", "error")
            return redirect(url_for("gym_auth.login_page"))
        return {"msg": "invalid token"}, 401

    app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2MB limit

    # import AFTER init
    from . import models
    from .routes import api_v1
    app.register_blueprint(api_v1)
    from gym_saas.app.routes.public import public_bp
    app.register_blueprint(public_bp)

    # init extensions (ONLY once)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("Database tables created")
    
    return app