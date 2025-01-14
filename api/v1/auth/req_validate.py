# api/v1/auth/req_validate.py

"""
Propagates errors to auth_routes invoked by UserRegistrationRequest
"""
import re

def validate_email(email: str) -> bool:
    # Simple email validation regex
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.fullmatch(email_regex, email) is not None

def validate_password(password: str) -> bool:
    # Example of password validation: At least 8 characters, 1 uppercase, 1 lowercase, 1 number
    min_length = 8
    if len(password) < min_length:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    return True
