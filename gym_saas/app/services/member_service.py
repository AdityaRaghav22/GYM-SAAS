from sqlalchemy import false
from gym_saas.app.extensions import db
from gym_saas.app.models import Gym, Member
from gym_saas.app.utils.validation import validate_id, validate_name, validate_phone_number
from gym_saas.app.utils.generate_id import generate_id
from sqlalchemy.exc import IntegrityError
from typing import Optional
from gym_saas.app.models import Membership


class MemberService:

  @staticmethod
  def create_member(gym_id, name, phone_number=None):
    if not all([gym_id, name]):
      return None, "All fields are required"

    gym_id_valid, gym_id_error = validate_id(gym_id)
    if not gym_id_valid:
      return None, gym_id_error

    gym = Gym.query.filter_by(id=gym_id, is_active=True).first()
    if not gym:
      return None, "Gym does not exist"

    name_valid, name_error = validate_name(name)
    if not name_valid:
      return None, name_error

    if phone_number:
      phone_valid, phone_error = validate_phone_number(phone_number)
      if not phone_valid:
        return None, phone_error

      existing_member = Member.query.filter(Member.gym_id == gym_id,
                                            Member.phone_number == phone_number,
                                            Member.is_active.is_(False)).first()
  
      if existing_member:
        existing_member.is_active = True
        db.session.commit()
        return None, "Member reactivated successfully"

    try:
      member = Member(id=generate_id(),
                      gym_id=gym_id,
                      name=name,
                      phone_number=phone_number or None)
      db.session.add(member)
      db.session.commit()
      return member, None

    except IntegrityError:
      db.session.rollback()
      return None, "Phone number already exists"

    except Exception as e:
      db.session.rollback()
      return None, str(e)

  @staticmethod
  def list_members(gym_id):
    gym_id_valid, gym_id_error = validate_id(gym_id)
    if not gym_id_valid:
      return None, gym_id_error

    gym = Gym.query.filter_by(id=gym_id).first()
    if not gym:
      return None, "Gym does not exist"

    members = Member.query.filter_by(gym_id=gym_id).order_by(Member.name.asc()).all()

    return members, None

  @staticmethod
  def get_member(gym_id, member_id):
    gym_id_valid, gym_id_error = validate_id(gym_id)
    if not gym_id_valid:
      return None, gym_id_error

    member_id_valid, member_id_error = validate_id(member_id)
    if not member_id_valid:
      return None, member_id_error

    member = Member.query.filter(
        Member.id == member_id,
        Member.gym_id == gym_id,
    ).first()

    if not member:
      return None, "Member does not exist"

    return member, None

  @staticmethod
  def update_member(gym_id,
                    member_id,
                    name: Optional[str] = None,
                    phone_number: Optional[str] = None):
    gym_id_valid, gym_id_error = validate_id(gym_id)
    if not gym_id_valid:
      return None, gym_id_error

    member_id_valid, member_id_error = validate_id(member_id)
    if not member_id_valid:
      return None, member_id_error

    member = Member.query.filter(Member.id == member_id,
                                 Member.gym_id == gym_id,
                                 Member.is_active.is_(True)).first()

    if not member:
      return None, "Member does not exist"

    if name is not None:
      name_valid, name_error = validate_name(name)
      if not name_valid:
        return None, name_error
      member.name = name

    if phone_number is not None:
      phone_valid, phone_error = validate_phone_number(phone_number)
      if not phone_valid:
        return None, phone_error

      phone_exists = Member.query.filter(Member.phone_number == phone_number,
                                         Member.gym_id == gym_id, Member.id
                                         != member_id).first()

      if phone_exists:
        return None, "Phone number already exists"

      member.phone_number = phone_number

    try:
      db.session.commit()
      return member, None

    except IntegrityError:
      db.session.rollback()
      return None, "Phone number already exists"

    except Exception:
      db.session.rollback()
      return None, "Something went wrong. Please try again."

  @staticmethod
  def deactivate_member(gym_id, member_id):
    gym_id_valid, gym_id_error = validate_id(gym_id)
    if not gym_id_valid:
      return None, gym_id_error

    member_id_valid, member_id_error = validate_id(member_id)
    if not member_id_valid:
      return None, member_id_error

    member = Member.query.filter(Member.id == member_id,
                                 Member.gym_id == gym_id,
                                 Member.is_active.is_(True)).first()

    if not member:
      return None, "Member does not exist"

    try:
      member.is_active = False
      Membership.query.filter(Membership.member_id == member_id,
                              Membership.gym_id == gym_id,
                              Membership.is_active.is_(True)).update(
                                  {
                                      Membership.is_active: False,
                                      Membership.status: "cancelled"
                                  },
                                  synchronize_session=False)
      db.session.commit()
      return member, None

    except Exception:
      db.session.rollback()
      return None, "Something went wrong. Please try again."


# -- ../routes/member.py
