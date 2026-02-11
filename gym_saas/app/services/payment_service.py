from gym_saas.app.extensions import db
from gym_saas.app.models import Membership, Gym, Payment
from gym_saas.app.utils.validation import validate_id
from gym_saas.app.utils.generate_id import generate_id
from decimal import Decimal, InvalidOperation
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func


class PaymentService:

  @staticmethod
  def create_payment(gym_id, membership_id, amount, payment_method):
    if not all([gym_id, membership_id, payment_method]):
      return None, "All fields are required"

    for value in [gym_id, membership_id]:
      valid, err = validate_id(value)
      if not valid:
        return None, err

    gym = Gym.query.filter_by(id=gym_id, is_active=True).first()
    if not gym:
      return None, "Gym does not exist"

    membership = Membership.query.filter(
        Membership.id == membership_id, Membership.gym_id == gym_id,
        Membership.is_active.is_(True)).first()
    if not membership:
      return None, "Membership does not exist"

    try:
      amount = Decimal(amount)
    except (InvalidOperation, TypeError):
      return None, "Invalid amount format"

    if amount <= 0:
      return None, "Amount must be greater than zero"

    if payment_method not in {"cash", "upi", "card"}:
      return None, "Invalid payment method"

    payment = Payment(id=generate_id(),
                      gym_id=gym_id,
                      membership_id=membership_id,
                      amount=amount,
                      payment_method=payment_method,
                      status="PAID")

    try:
      db.session.add(payment)
      db.session.commit()
      return payment, None
    except IntegrityError:
      db.session.rollback()
      return None, "Payment could not be processed"
    except Exception:
      db.session.rollback()
      return None, "Something went wrong. Please try again."

  @staticmethod
  def list_payments_by_gym(gym_id):
    valid, err = validate_id(gym_id)
    if not valid:
      return None, err

    payments = Payment.query.filter_by(gym_id=gym_id).order_by(
        Payment.created_at.desc()).all()

    return payments, None

  @staticmethod
  def list_payments_by_member(gym_id, member_id):
    for value in [gym_id, member_id]:
      valid, err = validate_id(value)
      if not valid:
        return None, err

    payments = Payment.query.join(Membership).filter(
        Membership.member_id == member_id,
        Payment.gym_id == gym_id).order_by(Payment.created_at.desc()).all()

    return payments, None

  @staticmethod
  def list_payments_by_plan(gym_id, plan_id):
    for value in [gym_id, plan_id]:
      valid, err = validate_id(value)
      if not valid:
        return None, err

    payments = Payment.query.join(Membership).filter(
        Membership.plan_id == plan_id,
        Payment.gym_id == gym_id).order_by(Payment.created_at.desc()).all()

    return payments, None

  @staticmethod
  def get_payment(gym_id, payment_id):
    for value in [gym_id, payment_id]:
      valid, err = validate_id(value)
      if not valid:
        return None, err

    payment = Payment.query.filter_by(id=payment_id, gym_id=gym_id).first()

    if not payment:
      return None, "Payment not found"

    return payment, None

  @staticmethod
  def get_revenue_summary(gym_id, start_date, end_date):
    valid, err = validate_id(gym_id)
    if not valid:
      return None, err

    total = db.session.query(func.coalesce(
        func.sum(Payment.amount),
        0)).filter(Payment.gym_id == gym_id, Payment.status == "PAID",
                   Payment.created_at.between(start_date, end_date)).scalar()
    return total, None

  @staticmethod
  def get_total_paid_for_membership(gym_id, membership_id) -> Decimal:
    total = (db.session.query(db.func.coalesce(db.func.sum(
        Payment.amount), 0)).filter(
            Payment.gym_id == gym_id,
            Payment.membership_id == membership_id,
        ).scalar())
  
    return total if total is not None else Decimal("0")
