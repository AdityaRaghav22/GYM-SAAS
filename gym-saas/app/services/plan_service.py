from app.extensions import db
from app.models import Gym, Plan
from app.utils.validation import (validate_id, validate_name,
                                  validate_duration_months, validate_price)
from app.utils.generate_id import generate_id
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
from typing import Optional


class PlanService:

  @staticmethod
  def create_plan(gym_id, name, duration_months, price, description=None):
    if not all([gym_id, name, duration_months, price]):
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

    try:
      duration_months = int(duration_months)

    except (TypeError, ValueError):
      return None, "Duration must be a positive integer"
      
    duration_valid, duration_error = validate_duration_months(duration_months)
    
    if not duration_valid:
      return None, duration_error

    try:
      price = Decimal(price)
      
    except (TypeError, ValueError):
      return None, "Price must be a positive number"
      
    price_valid, _, price_error = validate_price(price)
    
    if not price_valid:
      return None, price_error

    if description is not None and len(description) > 2000:
      return None, "Description cannot exceed 2000 characters"

    existing_plan = Plan.query.filter(Plan.gym_id == gym_id, Plan.name == name,
                                      Plan.is_active.is_(False)).first()

    if existing_plan:
      existing_plan.is_active = True
      db.session.commit()
      return None, "Plan reactivated successfully"

    try:
      plan = Plan(id=generate_id(),
                  gym_id=gym_id,
                  name=name,
                  duration_months=duration_months,
                  price=Decimal(price),
                  description=description)
      db.session.add(plan)
      db.session.commit()
      return plan, None

    except IntegrityError:
      db.session.rollback()
      return None, "Plan name already exists"

    except Exception as e:
      db.session.rollback()
      return None, str(e)

  @staticmethod
  def list_plans(gym_id):
    gym_id_valid, gym_id_error = validate_id(gym_id)
    if not gym_id_valid:
      return None, gym_id_error

    gym = Gym.query.filter_by(id=gym_id, is_active=True).first()
    if not gym:
      return None, "Gym does not exist"

    plans = Plan.query.filter(Plan.gym_id == gym_id,
                              Plan.is_active.is_(True)).all()

    return plans, None

  @staticmethod
  def get_plan(gym_id, plan_id):
    gym_id_valid, gym_id_error = validate_id(gym_id)
    if not gym_id_valid:
      return None, gym_id_error

    plan_id_valid, plan_id_error = validate_id(plan_id)
    if not plan_id_valid:
      return None, plan_id_error

    plan = Plan.query.filter(Plan.id == plan_id, Plan.gym_id == gym_id,
                             Plan.is_active.is_(True)).first()

    if not plan:
      return None, "Plan does not exist"

    return plan, None

  @staticmethod
  def update_plan(gym_id,
                  plan_id,
                  name: Optional[str] = None,
                  duration_months: Optional[int] = None,
                  price: Optional[Decimal] = None,
                  description: Optional[str] = None):
    gym_id_valid, gym_id_error = validate_id(gym_id)
    if not gym_id_valid:
      return None, gym_id_error

    plan_id_valid, plan_id_error = validate_id(plan_id)
    if not plan_id_valid:
      return None, plan_id_error

    plan = Plan.query.filter(Plan.id == plan_id, Plan.gym_id == gym_id,
                             Plan.is_active.is_(True)).first()

    if not plan:
      return None, "Plan does not exist"

    if name is not None:
      name_valid, name_error = validate_name(name)
      if not name_valid:
        return None, name_error

      name_exists = Plan.query.filter(Plan.name == name, Plan.gym_id == gym_id,
                                      Plan.id != plan_id).first()

      if name_exists:
        return None, "Plan name already exists"

      plan.name = name

    if duration_months is not None:
      duration_valid, duration_error = validate_duration_months(
          duration_months)
      if not duration_valid:
        return None, duration_error
      plan.duration_months = duration_months

    if price is not None:
      price_valid,_, price_error = validate_price(price)
      if not price_valid:
        return None, price_error
      plan.price = Decimal(price)

    if description is not None:
      if len(description) > 2000:
        return None, "Description cannot exceed 2000 characters"
      plan.description = description

    try:
      db.session.commit()
      return plan, None

    except IntegrityError:
      db.session.rollback()
      return None, "Plan name already exists"

    except Exception:
      db.session.rollback()
      return None, "Something went wrong. Please try again."

  @staticmethod
  def deactivate_plan(gym_id, plan_id):
    gym_id_valid, gym_id_error = validate_id(gym_id)
    if not gym_id_valid:
      return None, gym_id_error

    plan_id_valid, plan_id_error = validate_id(plan_id)
    if not plan_id_valid:
      return None, plan_id_error

    plan = Plan.query.filter(Plan.id == plan_id, Plan.gym_id == gym_id,
                             Plan.is_active.is_(True)).first()

    if not plan:
      return None, "Plan does not exist"

    plan.is_active = False

    try:
      db.session.commit()
      return plan, None

    except Exception:
      db.session.rollback()
      return None, "Something went wrong. Please try again."


# -- ./plan_service.py
