import decimal
from gym_saas.app.extensions import db
from gym_saas.app.models import Membership, Member, Plan
from gym_saas.app.services.payment_service import PaymentService
from gym_saas.app.utils.validation import validate_id, validate_price
from gym_saas.app.utils.generate_id import generate_id
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from decimal import Decimal


class MembershipService:

  @staticmethod
  def create_membership(gym_id, member_id, plan_id, start_date=None):
    if not all([gym_id, member_id, plan_id]):
      return None, "All fields are required"

    for value in [gym_id, member_id, plan_id]:
      valid, err = validate_id(value)
      if not valid:
        return None, err

    member = Member.query.filter(Member.id == member_id,
                                 Member.gym_id == gym_id,
                                 Member.is_active.is_(True)).first()
    if not member:
      return None, "Member does not exist"

    plan = Plan.query.filter(Plan.id == plan_id, Plan.gym_id == gym_id,
                             Plan.is_active.is_(True)).first()
    if not plan:
      return None, "Plan does not exist"

    # 🔒 Prevent multiple active memberships
    active = Membership.query.filter(Membership.member_id == member_id,
                                     Membership.gym_id == gym_id,
                                     Membership.is_active.is_(True)).first()
    if active:
      return None, "Member already has an active membership"

    # 📅 Parse start date
    if start_date:
      try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
      except ValueError:
        return None, "Invalid start date format"
    else:
      start_date = datetime.utcnow()

    # 🚫 Optional future-date restriction
    if start_date > datetime.utcnow() + timedelta(days=1):
      return None, "Start date cannot be in the future"

    end_date = start_date + relativedelta(months=plan.duration_months)

    status = "scheduled" if start_date > datetime.utcnow() else "active"

    membership = Membership(id=generate_id(),
                            gym_id=gym_id,
                            member_id=member_id,
                            plan_id=plan_id,
                            start_date=start_date,
                            end_date=end_date,
                            status=status,
                            is_active=True)

    try:
      db.session.add(membership)
      db.session.commit()
      return membership, None
    except Exception:
      db.session.rollback()
      return None, "Failed to create membership"

  @staticmethod
  def renew_membership(gym_id, membership_id, amount = None, payment_method = "cash"):
    for value in [gym_id, membership_id]:
      valid, err = validate_id(value)
      if not valid:
        return None, err

    membership = Membership.query.filter(
        Membership.id == membership_id, Membership.gym_id == gym_id).first()

    if not membership:
      return None, "Membership not found"

    plan = Plan.query.filter(Plan.id == membership.plan_id,
                             Plan.gym_id == gym_id,
                             Plan.is_active.is_(True)).first()

    if not plan:
      return None, "Plan not found"

    now = datetime.utcnow()
    grace_deadline = membership.end_date + timedelta(days=3)

    # auto-expire when end_date is crossed
    if membership.status == "active" and now >= membership.end_date:
      membership.status = "expired"
      db.session.commit()
      return None, "Membership expired"

    # Still active → cannot renew
    if now < membership.end_date:
      return None, "Membership is still active"

    # Grace period expired → cancel membership
    if now > grace_deadline:
      return MembershipService.deactivate_membership(gym_id, membership_id)

    new_start = now
    new_end = new_start + relativedelta(months=plan.duration_months)

    renewed = Membership(
      id=generate_id(),
      gym_id=gym_id,
      member_id=membership.member_id,
      plan_id=plan.id,
      start_date=new_start,
      end_date=new_end,
      status="active",
      is_active=True
    )

    try:
      membership.is_active = False
      membership.status = "cancelled"

      db.session.add(renewed)
      db.session.flush()  # 🔑 IMPORTANT

      # 🔐 PAYMENT LOGIC (balance-aware)
      if amount is None:
        amount = plan.price  # default full price

      if amount > 0:
         # 🔐 Create payment for the renewed membership
        amount = Decimal(amount)
        PaymentService.create_payment(
            gym_id=gym_id,
            membership_id=membership_id,
            amount=amount,
            payment_method=payment_method
        )

      db.session.commit()
      return renewed, None

    except Exception:
      db.session.rollback()
      return None, "Renewal failed"

  @staticmethod
  def list_active_memberships(gym_id):
    valid, err = validate_id(gym_id)
    if not valid:
      return None, err

    memberships = Membership.query.filter(Membership.gym_id == gym_id).all()

    updated = False
    for m in memberships:
      if MembershipService.sync_membership_status(m):
        updated = True

    if updated:
      db.session.commit()

    return memberships, None

  @staticmethod
  def list_active_memberships_for_member(gym_id, member_id):
    for value in [gym_id, member_id]:
      valid, err = validate_id(value)
      if not valid:
        return [], err

    memberships = Membership.query.filter(
        Membership.gym_id == gym_id, Membership.member_id == member_id, Membership.is_active.is_(True), ).all()

    updated = False
    for m in memberships:
      if MembershipService.sync_membership_status(m):
        updated = True

    if updated:
      db.session.commit()

    return memberships, None

  @staticmethod
  def get_membership(gym_id, membership_id):
    for value in [gym_id, membership_id]:
      valid, err = validate_id(value)
      if not valid:
        return None, err

    membership = Membership.query.filter(Membership.id == membership_id,
                                         Membership.gym_id == gym_id).first()

    if not membership:
      return None, "Membership not found"

    return membership, None

  @staticmethod
  def deactivate_membership(gym_id, membership_id):
    for value in [gym_id, membership_id]:
      valid, err = validate_id(value)
      if not valid:
        return None, err

    membership = Membership.query.filter(
        Membership.id == membership_id, Membership.gym_id == gym_id,
        Membership.is_active.is_(True)).first()
    if not membership:
      return None, "Membership not found"

    if membership.status == "cancelled":
      return None, "Membership already cancelled"

    grace_deadline = membership.end_date + timedelta(days=3)

    if datetime.utcnow() <= grace_deadline:
      return None, "Membership is in grace period. Cannot cancel yet."

    membership.is_active = False
    membership.status = "cancelled"

    try:
      db.session.commit()
      return membership, None
    except Exception:
      db.session.rollback()
      return None, "Something went wrong. Please try again."

  @staticmethod
  def sync_membership_status(membership):
    now = datetime.utcnow()
    grace_deadline = membership.end_date + timedelta(days=3)

    updated = False

    # 🔹 Active → Expired (grace starts)
    if membership.status == "active" and now >= membership.end_date:
      membership.status = "expired"
      updated = True

    # 🔹 Expired → Cancelled (grace over)
    if membership.status == "expired" and now > grace_deadline:
      membership.status = "cancelled"
      membership.is_active = False
      updated = True

    return updated

@staticmethod
def get_membership_balance(gym_id, membership):
  gym_id_valid, error = validate_id(gym_id)
  if not gym_id_valid:
    return None, error
  total_paid = PaymentService.get_total_paid_for_membership(
      gym_id, membership.id
  )
  return max(membership.plan.price - total_paid, 0)

# -- ../routes/membership.py
