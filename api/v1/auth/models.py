# /api/v1/auth/models.py

from pydantic import BaseModel, Field, field_validator
from fastapi import HTTPException
from api.v1.auth.req_validate import validate_password, validate_email

class UserRegistrationRequest(BaseModel):
    email: str = Field(..., description="The user's email address")
    password: str = Field(..., description="The user's password")

    @field_validator('email')
    def validate_email_field(cls, value):
        if not validate_email(value):
            raise HTTPException(status_code=400, detail='Invalid email format')
        return value

    @field_validator('password')
    def validate_password_field(cls, value):
        if not validate_password(value):
            raise HTTPException(status_code=400, detail='Password must be at least 8 characters long, include at least one uppercase letter, one lowercase letter, and one number')
        return value
