from app.models import User
from app.extensions import db, bcrypt
from app.utils.validation import validate_email, validate_password, validate_name, validate_role, validate_id, validate_phone_number
from app.utils.generate_id import generate_id
from sqlalchemy.exc import IntegrityError


# FUTURE FEATURE NO MORE BRAGGING 

class  UserService:
    @staticmethod
    def create_user(gym_id, name, email, phone_number, role):
      if not all([gym_id, name, email, phone_number, role]):
        return None, "All fields are required"

      user_id = generate_id()
      
      gym_id_valid, gym_id_error = validate_id(gym_id)

      if not gym_id_valid:
        return None, gym_id_error

      name_valid, name_error = validate_name(name)
      
      if not  name_valid:
        return None, name_error

      email_valid, email_error = validate_email(email)

      if not email_valid:
        return None, email_error

      existing = User.query.filter_by(email=email).first()

      if existing:
        return None, "Email already exists"
      
      phone_valid, phone_error = validate_phone_number(phone_number)

      if not phone_valid:
        return None, phone_error

      role_valid, role_error = validate_role(role)

      if not role_valid:
        return None, role_error

      try:
        user = User(
           id=user_id,
           gym_id=gym_id,
           name=name,
           email=email,
           phone_number=phone_number,
           role=role
        )
        db.session.add(user)
        db.session.commit()

      except IntegrityError:
        db.session.rollback()
        return None, "Email already exists"

      except Exception as e:
        db.session.rollback()
        return None, str(e)

    @staticmethod
    def delete_user(user_id):
      