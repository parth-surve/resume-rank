from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError

from app.core.config import settings

# Password hashing set-up

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password (plain_password: str) -> str:

    #     Plain password → bcrypt → hashed_password
    #     Used once, when a user is created.
    return pwd_context.hash(plain_password)

def verify_password (plain_password: str, hashed_password: str) -> bool:
    # Entered password -> compared with hashed_password -> True/False
    # Used on every login attempt.
    return pwd_context.verify (plain_password, hashed_password)


# JWT set up

def create_access_token (user_id: int, username: str, role: str) -> str:
    """
    User information -> JWT creation -> access token
    Called once, right after login is successful.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),          #"subject" - who this token belongs to
        "username": username,
        "role": role,
        "exp": expire                #jose checks this automically on decode
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm = settings.ALGORITHM)

def decode_access_token (token: str) -> dict:
    """
    JWT -> verify -> extract user information
    Raises JWTError if the token is invalid, tampered, or expired.
    Role checking itself happens one layer up, in deps.py.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])