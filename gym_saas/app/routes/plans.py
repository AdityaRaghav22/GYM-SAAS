from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from gym_saas.app.services.plan_service import PlanService
from gym_saas.app.services.membership_service import MembershipService
from gym_saas.app.services.payment_service import PaymentService
from gym_saas.app.utils.validation import validate_id
from decimal import Decimal

plan_bp = Blueprint("plan", __name__)

@plan_bp.route("/create", methods=["POST"])
@jwt_required()
def create_plan():
    gym_id = get_jwt_identity()
    valid, err = validate_id(gym_id)
    if not valid:
        flash(err or "Invalid gym ID", "error")
        return redirect(url_for("api_v1.dashboard.home"))

    
    data = request.form
    # duration_months = int(data.get("duration_months"))
    plan, error = PlanService.create_plan(
        gym_id,
        data.get("name"),
        data.get("duration_months"),
        data.get("price"),
        data.get("description"),
        free_months= data.get("free_months") or 0
    )

    if error:
        flash(error, "error")
        return redirect(url_for("api_v1.dashboard.home"))

    flash("Plan created successfully", "success")
    return redirect(url_for("api_v1.dashboard.home"))

@plan_bp.route("/list", methods=["GET"])
@jwt_required()
def list_plan():
    gym_id = get_jwt_identity()
    valid, err = validate_id(gym_id)
    if not valid:
        flash(err or "Invalid gym ID", "error")
        return redirect(url_for("api_v1.dashboard.home"))

    plans, error = PlanService.list_plans(gym_id)
    if error:
        flash(error, "error")
        return redirect(url_for("api_v1.dashboard.home"))

    return render_template("plan/list.html", plans=plans)

@plan_bp.route("/<plan_id>/details", methods=["GET"])
@jwt_required()
def plan_details(plan_id):
    gym_id = get_jwt_identity()

    for value in [gym_id, plan_id]:
        valid, err = validate_id(value)
        if not valid:
            flash(err or "Invalid ID", "error")
            return redirect(url_for("api_v1.plan.list_plan"))

    plan, error = PlanService.get_plan(gym_id, plan_id)
    if error:
        flash(error, "error")
        return redirect(url_for("api_v1.plan.list_plan"))

    memberships, error = MembershipService.list_active_memberships(gym_id)
    if error:
        flash(error, "error")
        return redirect(url_for("api_v1.plan.list_plan"))

    payments, error = PaymentService.list_payments_by_gym(gym_id)
    if error:
        flash(error, "error")
        return redirect(url_for("api_v1.plan.list_plan"))

    return render_template(
        "plan/plan_details.html",
        plan=plan,
        memberships=memberships,
        payments=payments,
    )

@plan_bp.route("/<plan_id>/update", methods=["POST"])
@jwt_required()
def update_plan(plan_id):
    gym_id = get_jwt_identity()

    for value in [gym_id, plan_id]:
        valid, err = validate_id(value)
        if not valid:
            flash(err or "Invalid ID", "error")
            return redirect(
                url_for("api_v1.plan.plan_details", plan_id=plan_id)
            )

    data = request.form
    raw_duration = data.get("duration_months")

    try:
        duration_months = int(raw_duration) if raw_duration else None
    except Exception:
        flash("Invalid duration format", "error")
        return redirect(
            url_for("api_v1.plan.plan_details", plan_id=plan_id)
        )

    raw_price = data.get("price")
    try:
        price = Decimal(raw_price) if raw_price else None
    except Exception:
        flash("Invalid price format", "error")
        return redirect(
            url_for("api_v1.plan.plan_details", plan_id=plan_id)
        )

    plan, error = PlanService.update_plan(
        gym_id,
        plan_id,
        data.get("name"),
        duration_months,
        price,
        data.get("description"),
    )

    if error:
        flash(error, "error")
    else:
        flash("Plan updated successfully", "success")

    return redirect(
        url_for("api_v1.plan.plan_details", plan_id=plan_id)
    )

@plan_bp.route("/<plan_id>/deactivate", methods=["POST"])
@jwt_required()
def deactivate_plan(plan_id):
    gym_id = get_jwt_identity()

    for value in [gym_id, plan_id]:
        valid, err = validate_id(value)
        if not valid:
            flash(err or "Invalid ID", "error")
            return redirect(url_for("api_v1.plan.list_plan"))

    plan, error = PlanService.deactivate_plan(gym_id, plan_id)
    if error:
        flash(error, "error")
    else:
        flash("Plan deactivated successfully", "success")

    return redirect(url_for("api_v1.plan.list_plan"))
