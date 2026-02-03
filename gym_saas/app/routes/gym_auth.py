from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    verify_jwt_in_request
)
from gym_saas.app.services.gym_auth_service import GymAuthService
from gym_saas.app.utils.route_validation import validate_register, validate_login
from typing import cast

gym_auth_bp = Blueprint("gym_auth", __name__)

# =========================
# GET PAGES
# =========================

@gym_auth_bp.route("/register", methods=["GET"])
def register_page():
    try:
        verify_jwt_in_request()
        return redirect(url_for("api_v1.dashboard.home"))
    except:
        return render_template("gym/register.html")

@gym_auth_bp.route("/login", methods=["GET"])
def login_page():
    try:
        verify_jwt_in_request()
        return redirect(url_for("api_v1.dashboard.home"))
    except:
        return render_template("gym/login.html")
    
    
# =========================
# AUTH ACTIONS
# =========================


@gym_auth_bp.route("/register", methods=["POST"])
def register():
    data = request.form
    errors = validate_register(data)

    if errors:
        flash("Invalid credentials. Please try again.", "error")
        return render_template("gym/register.html")

    gym, error = GymAuthService.register_gym(
        name=data.get("name"),
        phone=data.get("phone"),
        email=data.get("email"),
        password=data.get("password"),
    )

    if error:
        flash(error, "error")
        return render_template("gym/register.html")

    flash("Registration successful. Please log in.", "success")
    return redirect(url_for("api_v1.gym_auth.login_page"))

@gym_auth_bp.route("/login", methods=["POST"])
def login():
    data = request.form
    errors = validate_login(data)

    if errors:
        flash("Invalid login data.", "error")
        return render_template("gym/login.html")

    tokens, error = GymAuthService.login_gym(
        email=data.get("email"),
        password=data.get("password"),
    )

    if error or not tokens:
        flash(error or "Authentication failed.", "error")
        return render_template("gym/login.html")

    response = redirect(url_for("api_v1.dashboard.home"))
    response = cast(Response, response)

    set_access_cookies(response, tokens["access_token"])
    set_refresh_cookies(response, tokens["refresh_token"])
    
    return response

@gym_auth_bp.route("/logout", methods=["POST"])
def logout():
    response = redirect(url_for("api_v1.gym_auth.login_page"))
    response = cast(Response, response)
    unset_jwt_cookies(response)
    flash("Logged out successfully.", "success")
    return response

# =========================
# PROFILE
# =========================

@gym_auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    gym_id = get_jwt_identity()
    gym, error = GymAuthService.get_gym(gym_id)

    if error:
        flash(error, "error")
        return redirect(url_for("api_v1.dashboard.home"))

    return render_template("gym/profile.html", gym=gym)

@gym_auth_bp.route("/update", methods=["POST"])
@jwt_required()
def update():
    gym_id = get_jwt_identity()
    data = request.form

    result, error = GymAuthService.update_gym(
        gym_id=gym_id,
        name=data.get("name"),
        phone_number=data.get("phone"),
        email=data.get("email"),
    )

    if error:
        flash(error, "error")
    elif result:
        flash(result["message"], "success")
    else:
        flash("Update Failed.", "error")

    return redirect(url_for("api_v1.gym_auth.profile"))

@gym_auth_bp.route("/delete", methods=["POST"])
@jwt_required()
def delete():
    gym_id = get_jwt_identity()

    result, error = GymAuthService.delete_gym(gym_id)

    if error:
        flash(error, "error")
        return redirect(url_for("api_v1.gym_auth.profile"))

    if result is None:
        flash("Failed to delete gym.", "error")
        return redirect(url_for("api_v1.gym_auth.profile"))

    response = redirect(url_for("api_v1.gym_auth.login_page"))
    unset_jwt_cookies(response)
    flash(result["message"], "success")
    return response

@gym_auth_bp.route("/refresh", methods=["GET"])
@jwt_required(refresh=True)
def refresh():
    print("Hello refresh here")
    identity = get_jwt_identity()

    # Create new access token directly
    access_token = create_access_token(identity=identity)

    # 🔑 Redirect BACK to where user came from
    next_url = request.args.get("next") or url_for("api_v1.dashboard.home")

    response = redirect(next_url)
    set_access_cookies(response, access_token)
    
    return response

