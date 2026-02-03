from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended.exceptions import JWTExtendedException

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def home():
    try:
        verify_jwt_in_request()  # STRICT validation
        return redirect(url_for("api_v1.dashboard.home"))
    except JWTExtendedException:
        return render_template("home.html")