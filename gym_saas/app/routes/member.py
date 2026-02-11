from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from gym_saas.app.extensions import db
from gym_saas.app.models import Membership
from gym_saas.app.services.member_service import MemberService
from gym_saas.app.services.membership_service import MembershipService
from gym_saas.app.services.payment_service import PaymentService
from gym_saas.app.services.plan_service import PlanService
from gym_saas.app.utils.validation import validate_id

member_bp = Blueprint("member", __name__)

@member_bp.route("/create", methods=["POST"])
@jwt_required()
def create_member():
    gym_id = get_jwt_identity()
    valid, err = validate_id(gym_id)
    if not valid:
        flash(err or "Invalid gym ID", "error")
        return redirect(url_for("api_v1.dashboard.home"))

    data = request.form
    member, error = MemberService.create_member(
        gym_id,
        data.get("name"),
        data.get("phone_number")
    )

    if error:
        flash(error, "error")
        return redirect(url_for("api_v1.dashboard.home"))

    flash("Member created successfully", "success")
    return redirect(url_for("api_v1.dashboard.home"))


@member_bp.route("/list", methods=["GET"])
@jwt_required()
def list_member():
    gym_id = get_jwt_identity()
    valid, err = validate_id(gym_id)
    if not valid:
        flash(err or "Invalid gym ID", "error")
        return redirect(url_for("api_v1.dashboard.home"))

    members, error = MemberService.list_members(gym_id)
    if error:
        flash(error, "error")
        return redirect(url_for("api_v1.dashboard.home"))

    return render_template("member/list.html", members=members)


@member_bp.route("/<member_id>/details", methods=["GET", "POST"])
@jwt_required()
def member_details(member_id):
    gym_id = get_jwt_identity()

    # --- ID validation ---
    for value in (gym_id, member_id):
        valid, err = validate_id(value)
        if not valid:
            flash(err or "Invalid ID", "error")
            return redirect(url_for("api_v1.member.list_member"))

    # --- Member ---
    member, error = MemberService.get_member(gym_id, member_id)
    if error:
        flash(error, "error")
        return redirect(url_for("api_v1.member.list_member"))

    # --- CLEAR BALANCE (POST ONLY) ---
    if request.method == "POST" and request.form.get("clear_balance") == "true":
        membership = Membership.query.filter_by(
            gym_id=gym_id,
            member_id=member_id,
            is_active=True
        ).first()

        if not membership:
            flash("No active membership found", "error")
            return redirect(request.url)

        if membership.balance_amount <= 0:
            flash("No balance to clear", "info")
            return redirect(request.url)

        PaymentService.create_payment(
            gym_id=gym_id,
            membership_id=membership.id,
            amount=membership.balance_amount,   # backend authority
            payment_method=request.form.get("payment_method", "cash")
        )

        membership.paid_amount += membership.balance_amount
        membership.balance_amount = 0

        db.session.commit()

        flash("Balance cleared successfully", "success")
        return redirect("api_v1.member.list_member")

    # --- Memberships (READ ONLY) ---
    memberships, error = MembershipService.list_active_memberships_for_member(
        gym_id, member_id
    )
    if error:
        flash(error, "error")
        return redirect(url_for("api_v1.member.list_member"))

    memberships = memberships or []

    # --- Totals ---
    overall_plan_total = 0
    overall_paid = 0
    overall_balance = 0

    for m in memberships:
        total_paid = PaymentService.get_total_paid_for_membership(gym_id, m.id)
        plan_amount = m.plan.price

        overall_plan_total += plan_amount
        overall_paid += total_paid
        overall_balance += max(plan_amount - total_paid, 0)

    payments, _ = PaymentService.list_payments_by_member(gym_id, member_id)
    plans, _ = PlanService.list_plans(gym_id)

    return render_template(
        "member/member_details.html",
        member=member,
        memberships=memberships,
        payments=payments or [],
        plans=plans,
        overall_plan_total=overall_plan_total,
        overall_paid=overall_paid,
        overall_balance=overall_balance
    )


@member_bp.route("/<member_id>/update", methods=["POST"])
@jwt_required()
def update_member(member_id):
    gym_id = get_jwt_identity()

    for value in [gym_id, member_id]:
        valid, err = validate_id(value)
        if not valid:
            flash(err or "Invalid ID", "error")
            return redirect(
                url_for("api_v1.member.member_details", member_id=member_id)
            )

    data = request.form
    member, error = MemberService.update_member(
        gym_id,
        member_id,
        data.get("name"),
        data.get("phone_number"),
    )

    if error:
        flash(error, "error")
    else:
        flash("Member updated successfully", "success")

    return redirect(
        url_for("api_v1.member.member_details", member_id=member_id)
    )


@member_bp.route("/<member_id>/deactivate", methods=["POST"])
@jwt_required()
def deactivate_member(member_id):
    gym_id = get_jwt_identity()

    for value in [gym_id, member_id]:
        valid, err = validate_id(value)
        if not valid:
            flash(err or "Invalid ID", "error")
            return redirect(url_for("api_v1.member.list_member"))

    member, error = MemberService.deactivate_member(gym_id, member_id)
    if error:
        flash(error, "error")
    else:
        flash("Member deactivated successfully", "success")

    return redirect(url_for("api_v1.member.list_member"))
