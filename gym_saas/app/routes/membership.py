from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from gym_saas.app.services.membership_service import MembershipService
from gym_saas.app.services.payment_service import PaymentService
from gym_saas.app.services.plan_service import PlanService
from gym_saas.app.utils.validation import validate_id

membership_bp = Blueprint("membership", __name__)


@membership_bp.route("/create", methods=["POST"])
@jwt_required()
def create_membership():
    gym_id = get_jwt_identity()
    data = request.form

    member_id = data.get("member_id")
    plan_id = data.get("plan_id")
    payment_method = data.get("payment_method")
    

    for value in [gym_id, member_id, plan_id]:
        valid, err = validate_id(value)
        if not valid:
            flash(err or "Invalid ID", "error")
            return redirect(url_for("api_v1.dashboard.home"))

    start_date = data.get("start_date")
    
    membership, error = MembershipService.create_membership(
        gym_id, member_id, plan_id, start_date)

    if error:
        flash(error, "error")
        return redirect(url_for("api_v1.dashboard.home"))

    if membership is None:
        flash("Failed to create membership", "error")
        return redirect(url_for("api_v1.dashboard.home"))

    plan, error = PlanService.get_plan(gym_id, plan_id)
    if error:
        flash(error, "error")
        return redirect(url_for("api_v1.dashboard.home"))

    if plan is None:
        flash("Plan not found", "error")
        return redirect(url_for("api_v1.dashboard.home"))

    payment, error = PaymentService.create_payment(
        gym_id,
        membership.id,
        plan.price,
        payment_method
    )

    if error:
        MembershipService.deactivate_membership(gym_id, membership.id)
        flash(error, "error")
        return redirect(url_for("api_v1.dashboard.home"))

    flash("Membership created successfully", "success")
    return redirect(url_for("api_v1.dashboard.home"))


@membership_bp.route("/list", methods=["GET"])
@jwt_required()
def list_membership():
    gym_id = get_jwt_identity()
    valid, err = validate_id(gym_id)
    if not valid:
        flash(err or "Invalid gym ID", "error")
        return redirect(url_for("api_v1.dashboard.home"))

    memberships, error = MembershipService.list_active_memberships(gym_id)
    if error:
        flash(error, "error")
        return redirect(url_for("api_v1.dashboard.home"))

    return render_template("membership/list.html", memberships=memberships)

@membership_bp.route("/<membership_id>/renew", methods=["POST"])
@jwt_required()
def renew_membership(membership_id):
    gym_id = get_jwt_identity()

    for value in [gym_id, membership_id]:
        valid, err = validate_id(value)
        if not valid:
            flash(err or "Invalid ID", "error")
            return redirect(url_for("api_v1.membership.list_membership"))

    membership, error = MembershipService.renew_membership(
        gym_id, membership_id
    )

    if error:
        flash(error, "error")
        return redirect(url_for("api_v1.membership.list_membership"))

    if membership is None:
        flash("Failed to renew membership", "error")
        return redirect(url_for("api_v1.membership.list_membership"))

    plan, error = PlanService.get_plan(gym_id, membership.plan_id)
    if error:
        flash(error, "error")
        return redirect(url_for("api_v1.membership.list_membership"))

    if plan is None:
        flash("Plan not found", "error")
        return redirect(url_for("api_v1.membership.list_membership"))

    payment_method = request.form.get("payment_method")

    payment, error = PaymentService.create_payment(
        gym_id,
        membership.id,
        plan.price,
        payment_method
    )

    if error:
        flash(error, "error")
        return redirect(url_for("api_v1.membership.list_membership"))

    flash("Membership renewed successfully", "success")
    return redirect(url_for("api_v1.membership.list_membership"))


@membership_bp.route("/<membership_id>/deactivate", methods=["POST"])
@jwt_required()
def deactivate_membership(membership_id):
    gym_id = get_jwt_identity()

    for value in [gym_id, membership_id]:
        valid, err = validate_id(value)
        if not valid:
            flash(err or "Invalid ID", "error")
            return redirect(url_for("api_v1.membership.list_membership"))

    membership, error = MembershipService.deactivate_membership(
        gym_id, membership_id
    )

    if error:
        flash(error, "error")
    else:
        flash("Membership deactivated successfully", "success")

    return redirect(url_for("api_v1.membership.list_membership"))
