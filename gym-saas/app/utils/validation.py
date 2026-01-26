import re
import uuid
from datetime import datetime

def validate_email(email):
  pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

  if not re.match(pattern, email):
    return False, "Invalid email format"
  return True, None

def validate_phone_number(phone_number):
  pattern = r'^\d{10}$'
  if not re.match(pattern, phone_number):
    return False, "Invalid phone number format"
  return True, None  

def validate_password(password):
  if len(password) < 8:
    return False, "Password must be at least 8 characters long"
  if not any(char.isdigit() for char in password):
    return False, "Password must contain at least one digit"
  return True, None

def validate_name(name):
  name = name.strip()
  if len(name) < 2:
    return False, "Name must be at least 2 characters long"
  if not name.replace(" ", "").isalpha():
    return False, "Name must contain only letters"
  return True, None

def validate_id(value):
  try:
    uuid.UUID(value)
    return True, None
  except ValueError:
    return False, "Invalid ID format"

def validate_role(role):
  if role not in ["owner", "staff"]:
    return False, "Invalid role"
  return True, None


def validate_duration_months(duration_months):
  if not isinstance(duration_months, int) or duration_months <= 0:
    return False, "Duration must be a positive integer"

  if duration_months > 12:
    return False, "Duration cannot exceed 12 months"

  return True, None

def  validate_price(price):
  if not isinstance(price, (int, float)) or price <= 0:
     return False, "Price must be a positive number"

  return True, None

def validate_date(date_str):
  try:
     datetime.strptime(date_str, "%Y-%m-%d")
     return True, None
  except ValueError:
     return False, "Invalid date format. Use YYYY-MM-DD"
