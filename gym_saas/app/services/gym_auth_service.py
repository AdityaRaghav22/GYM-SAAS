from gym_saas.app.extensions import db, bcrypt
from gym_saas.app.models import Gym
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
from gym_saas.app.utils.validation import (validate_email, validate_password,
                                           validate_phone_number,
                                           validate_name)
from gym_saas.app.utils.generate_id import generate_id
from sqlalchemy.exc import IntegrityError
import secrets
from datetime import datetime


class GymAuthService:

    @staticmethod
    def register_gym(name, phone, email, password):
        if not all([name, phone, email, password]):
            return None, "All fields are required"

        email = email.strip().lower()

        name_valid, name_error = validate_name(name)
        if not name_valid:
            return None, name_error

        phone_valid, phone_error = validate_phone_number(phone)
        if not phone_valid:
            return None, phone_error

        email_valid, email_error = validate_email(email)
        if not email_valid:
            return None, email_error

        password_valid, password_error = validate_password(password)
        if not password_valid:
            return None, password_error

        existing = Gym.query.filter((Gym.email == email)
                                    | (Gym.phone_number == phone)).first()
        if existing:
            return None, "Email or phone number already exists"

        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

        try:
            gym = Gym(
                id=generate_id(),
                name=name,
                phone_number=phone,
                email=email,
                password_hash=password_hash,
            )
            db.session.add(gym)
            db.session.commit()
            return gym, None

        except IntegrityError:
            db.session.rollback()
            return None, "Email or phone number already exists"

        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def login_gym(email, password):
        if not all([email, password]):
            return None, "Email and password are required"

        email = email.strip().lower()
        email_valid, email_error = validate_email(email)
        if not email_valid:
            return None, email_error

        gym = Gym.query.filter_by(email=email, is_active=True).first()

        print(password)

        if not gym or not bcrypt.check_password_hash(gym.password_hash,
                                                     password):
            return None, "Invalid email or password"

        access_token = create_access_token(identity=gym.id,
                                           additional_claims={
                                               "gym_id": gym.id,
                                               "is_active": gym.is_active
                                           },
                                           expires_delta=timedelta(minutes=15))
        refresh_token = create_refresh_token(identity=gym.id,
                                             expires_delta=timedelta(days=30))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }, None

    @staticmethod
    def refresh_access_token(identity):
        gym = db.session.get(Gym, identity)

        if not gym or not gym.is_active:
            return None, "Invalid session"

        new_access_token = create_access_token(
            identity=gym.id, expires_delta=timedelta(minutes=15))

        return new_access_token, None

    @staticmethod
    def delete_gym(gym_id):
        gym = db.session.get(Gym, gym_id)
        if not gym:
            return None, "Gym not found"

        try:
            gym.is_active = False
            db.session.commit()
            return {"message": "Gym deleted successfully"}, None

        except Exception:
            db.session.rollback()
            return None, "Something went wrong. Please try again."

    @staticmethod
    def get_gym(gym_id):
        gym = db.session.get(Gym, gym_id)

        if not gym:
            return None, "Gym not found"

        if not gym.is_active:
            return None, "Gym account is inactive"

        return gym, None

    @staticmethod
    def update_gym(gym_id, name=None, phone_number=None, email=None):
        gym = db.session.get(Gym, gym_id)
        if not gym:
            return None, "Gym not found"

        if name:
            name_valid, name_error = validate_name(name)
            if not name_valid:
                return None, name_error
            gym.name = name

        if phone_number:
            phone_valid, phone_error = validate_phone_number(phone_number)
            if not phone_valid:
                return None, phone_error

            phone_exists = Gym.query.filter(Gym.phone_number == phone_number,
                                            Gym.id != gym_id).first()

            if phone_exists:
                return None, "Phone number already exists"

            gym.phone_number = phone_number

        if email:
            email = email.strip().lower()
            email_valid, email_error = validate_email(email)
            if not email_valid:
                return None, email_error

            email_exists = Gym.query.filter(Gym.email == email, Gym.id
                                            != gym_id).first()

            if email_exists:
                return None, "Email already exists"

            gym.email = email

        try:
            db.session.commit()
            return {"message": "Gym updated successfully"}, None

        except IntegrityError:
            db.session.rollback()
            return None, "Email or phone number already exists"

        except Exception:
            db.session.rollback()
            return None, "Something went wrong. Please try again."

    @staticmethod
    def generate_reset_link_for_admin(email):

        if not email:
            return None, "Email is required"

        email = email.strip().lower()

        gym = Gym.query.filter_by(email=email, is_active=True).first()

        if not gym:
            return None, "Gym not found"

        # generate secure token
        token = secrets.token_urlsafe(32)

        gym.reset_token = token
        gym.reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)

        try:
            db.session.commit()

            reset_link = f"https://gym-saas.onrender.com/gym/account-recovery/?t={token}"

            return {"reset_link": reset_link, "expires_in": "15 minutes"}, None

        except Exception:
            db.session.rollback()
            return None, "Something went wrong"


    @staticmethod
    def set_reset_password(token, new_password):
    
        from urllib.parse import unquote
        from datetime import datetime, timezone
    
        token = unquote(token).strip()
    
        gym = Gym.query.filter_by(reset_token=token).first()
    
        if not gym:
            return None, "Invalid reset link"
    
        if gym.reset_token is None:
            return None, "Reset link already used"
    
        if not gym.reset_token_expiry or gym.reset_token_expiry < datetime.now(
                timezone.utc):
            return None, "Reset link expired"
    
        password_valid, password_error = validate_password(new_password)
        if not password_valid:
            return None, password_error
    
        new_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
    
        try:
            gym.password_hash = new_hash
            gym.reset_token = None
            gym.reset_token_expiry = None
    
            db.session.commit()
    
            return {"message": "Password reset successful"}, None
    
        except Exception as e:
            db.session.rollback()
            print("RESET PASSWORD ERROR:", e)
            return None, "Something went wrong. Please try again."
    
# -- ../services/membership_service.py
