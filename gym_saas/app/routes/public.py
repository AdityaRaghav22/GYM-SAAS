from flask import Blueprint, render_template
from gym_saas.app.services.gym_auth_service import GymAuthService
from flask import redirect, url_for

public_bp = Blueprint("public", __name__)

@public_bp.route("/")
def home():
    if GymAuthService.has_valid_refresh():
        return redirect(url_for("api_v1.dashboard.home"))
        
    return render_template("home.html")
