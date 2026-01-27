from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/", methods=["GET"])
@jwt_required()
def home():
    return render_template("api_v1.dashboard.home")
