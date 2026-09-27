import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app.db.models import User
from app.db.database import get_db                     # confirm path w/ db member
from app.services.auth_service import AuthService
from app.core.security import verify_password,create_access_token,decode_access_token

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        logger.warning("Authentication failed: invalid or expired token")
        raise credentials_exception

    user = AuthService(db).get_user_by_id(int(user_id))
    if user is None:
        logger.warning(
            "Authentication failed: token references missing user_id=%s",
            user_id,
        )
        raise credentials_exception
    return user


def require_role(*allowed_roles: str):
    def role_checker(current_user = Depends(get_current_user)):
        if current_user.role.value not in allowed_roles:
            logger.warning(
                "Authorization failed: user_id=%s role=%s required_roles=%s",
                current_user.id,
                current_user.role.value,
                allowed_roles,
            )
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions",
            )
        return current_user

    return role_checker