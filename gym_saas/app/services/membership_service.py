from gym_saas.app.extensions import db
from gym_saas.app.models import Membership, Member, Plan
from gym_saas.app.utils.validation import validate_id
from gym_saas.app.utils.generate_id import generate_id
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta


class MembershipService:

  @staticmethod
  def create_membership(gym_id, member_id, plan_id):
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

    existing = Membership.query.filter(Membership.member_id == member_id,
                                       Membership.gym_id == gym_id,
                                       Membership.is_active.is_(False)).first()
    if existing:
      existing.is_active = True
      db.session.commit()
      return None, "Membership activated successfully"

    start_date = datetime.utcnow()
    end_date = start_date + relativedelta(months=plan.duration_months)

    membership = Membership(id=generate_id(),
                            gym_id=gym_id,
                            member_id=member_id,
                            plan_id=plan_id,
                            start_date=start_date,
                            end_date=end_date,
                            status="active",
                            is_active=True)

    try:
      db.session.add(membership)
      db.session.commit()
      return membership, None
    except Exception:
      db.session.rollback()
      return None, "Failed to create membership"

  @staticmethod
  def renew_membership(gym_id, membership_id):
    for value in [gym_id, membership_id]:
      valid, err = validate_id(value)
      if not valid:
        return None, err

    membership = Membership.query.filter(
        Membership.id == membership_id, Membership.gym_id == gym_id,
        Membership.is_active.is_(True)).first()
    if not membership:
      return None, "Active membership not found"

    plan = Plan.query.filter(Plan.id == membership.plan_id,
                             Plan.gym_id == gym_id,
                             Plan.is_active.is_(True)).first()
    if not plan:
      return None, "Plan not found"

    now = datetime.utcnow()
    grace_deadline = membership.end_date + timedelta(days=3)

    if now > grace_deadline:
      membership.is_active = False
      membership.status = "expired"
      db.session.commit()
      return None, "Renewal period expired"

    new_start = max(now, membership.end_date)
    new_end = new_start + relativedelta(months=plan.duration_months)

    renewed = Membership(id=generate_id(),
                         gym_id=gym_id,
                         member_id=membership.member_id,
                         plan_id=plan.id,
                         start_date=new_start,
                         end_date=new_end,
                         status="active",
                         is_active=True)

    try:
      membership.is_active = False
      membership.status = "expired"
      db.session.add(renewed)
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

    memberships = Membership.query.filter(
        Membership.gym_id == gym_id).all()

    return memberships, None

  @staticmethod
  def list_active_memberships_for_member(gym_id, member_id):
    for value in [gym_id, member_id]:
      valid, err = validate_id(value)
      if not valid:
        return None, err

    memberships = Membership.query.filter(
        Membership.gym_id == gym_id, Membership.member_id == member_id,
        Membership.is_active.is_(True)).all()

    return memberships, None

  @staticmethod
  def get_membership(gym_id, membership_id):
    for value in [gym_id, membership_id]:
      valid, err = validate_id(value)
      if not valid:
        return None, err

    membership = Membership.query.filter(
        Membership.id == membership_id, Membership.gym_id == gym_id).first()

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
        Membership.member_id.status == "active",
        Membership.is_active.is_(True)).first()
    if not membership:
      return None, "Membership not found"

    if membership.status == "cancelled":
      return None, "Membership already cancelled"

    if datetime.utcnow() >= membership.end_date - timedelta(days=3):
      return None, "Membership cannot be cancelled within 3 days of expiry"

    membership.is_active = False
    membership.status = "cancelled"

    try:
      db.session.commit()
      return membership, None
    except Exception:
      db.session.rollback()
      return None, "Something went wrong. Please try again."


# -- ../routes/membership.py
