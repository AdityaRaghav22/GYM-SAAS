from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def home():
    verify_jwt_in_request(optional=True)
    if get_jwt_identity():
        return redirect(url_for("dashboard.dashboard_home"))
    return render_template("home.html")
