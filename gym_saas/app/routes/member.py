from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
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


@member_bp.route("/<member_id>/details", methods=["GET"])
@jwt_required()
def member_details(member_id):
    gym_id = get_jwt_identity()

    for value in [gym_id, member_id]:
        valid, err = validate_id(value)
        if not valid:
            flash(err or "Invalid ID", "error")
            return redirect(url_for("api_v1.member.list_member"))

    member, error = MemberService.get_member(gym_id, member_id)
    if error:
        flash(error, "error")
        return redirect(url_for("api_v1.member.list_member"))

    memberships, error = MembershipService.list_active_memberships_for_member(
        gym_id, member_id
    )
    if error:
        flash(error, "error")
        return redirect(url_for("api_v1.member.list_member"))
        
    payments, error = PaymentService.list_payments_by_member(gym_id, member_id)
    if error:
        flash(error, "error")
        return redirect(url_for("api_v1.member.list_member"))

    plans, _ = PlanService.list_plans(gym_id)

    membership_balances = {}

    for m in memberships:
        total_paid = PaymentService.get_total_paid_for_membership(
            gym_id, m.id
        )

        plan_amount = m.plan.price  # assuming relationship exists
        balance = plan_amount - total_paid

        membership_balances[m.id] = {
            "plan_amount": plan_amount,
            "paid": total_paid,
            "balance": balance,
        }

    overall_plan_total = sum(
        data["plan_amount"] for data in membership_balances.values()
    )
    overall_paid = sum(
        data["paid"] for data in membership_balances.values()
    )
    overall_balance = sum(
        data["balance"] for data in membership_balances.values()
    )

    return render_template(
        "member/member_details.html",
        member=member,
        memberships=memberships,
        payments=payments,
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
