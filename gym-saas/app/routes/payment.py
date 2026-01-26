from flask import Blueprint, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.payment_service import PaymentService
from app.services.membership_service import MembershipService
from app.utils.validation import validate_id

payment_bp = Blueprint("payment", __name__)


@payment_bp.route("/list", methods=["GET"])
@jwt_required()
def list_payment():
    gym_id = get_jwt_identity()

    valid, err = validate_id(gym_id)
    if not valid:
        flash(err or "error")
        return redirect(url_for("api_v1.dashboard.home"))

    payments, error = PaymentService.list_payments_by_gym(gym_id)

    if error:
        flash(error, "error")
        return redirect(url_for("api_v1.dashboard.home"))

    return render_template("payment/list.html", payments=payments)


@payment_bp.route("/<payment_id>/details", methods=["GET"])
@jwt_required()
def payment_details(payment_id):
    gym_id = get_jwt_identity()

    valid, err = validate_id(gym_id)
    if not valid:
        flash(err or "error")
        return redirect(url_for("api_v1.payment.list_payment"))

    valid, err = validate_id(payment_id)
    if not valid:
        flash(err or "error")
        return redirect(url_for("api_v1.payment.list_payment"))

    payment, error = PaymentService.get_payment(gym_id, payment_id)

    if payment is None:
        flash(error or "Payment not found", "error")
        return redirect(url_for("api_v1.payment.list_payment"))

    membership, error = MembershipService.get_membership(
        gym_id, payment.membership_id
    )

    if membership is None:
        flash(error or "Membership not found", "error")
        return redirect(url_for("api_v1.payment.list_payment"))

    return render_template(
        "payment/payment_details.html",
        payment=payment,
        membership=membership
    )
