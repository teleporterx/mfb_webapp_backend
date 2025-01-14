# /api/v1/auth/auth_security.py

from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt

from api.v1.config import CONFIG

SECRET_KEY = CONFIG['JWT_SECRET_KEY']  # Make sure to set this in your config
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiration time

# Create a password hashing context using bcrypt or Argon2 (depending on your choice)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthSecurity:
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash the given password.

        Args:
            password (str): The plaintext password to hash.

        Returns:
            str: The hashed password.
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify the given password against the hashed password.

        Args:
            plain_password (str): The plaintext password.
            hashed_password (str): The hashed password.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta  # Updated line
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # Updated line
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt