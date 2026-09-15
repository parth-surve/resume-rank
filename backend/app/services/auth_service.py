# the actual login logic
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.models.user import User          # need to confirm this path w/ db member
from app.core.security import verify_password, create_access_token


class AuthService:
    # this class handles all the login stuff / user lookups
    # routes should call this, not touch User model directly

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_identifier(self, identifier: str) -> User | None:
        # identifier = username OR email, checking both
        # only used during login
        return (
            self.db.query(User)
            .filter(or_(User.username == identifier, User.email == identifier))
            .first()
        )

    def get_user_by_id(self, user_id: int) -> User | None:
        # this one i'll use later in deps.py
        # to get the user back from the id stored in the jwt (sub)
        return self.db.query(User).filter(User.id == user_id).first()

    def authenticate(self, identifier: str, password: str) -> str | None:
        # main login function
        # flow: find user by identifier -> check password -> make jwt -> return token
        # if anything fails just return None

        user = self.get_user_by_identifier(identifier)

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None
        # not saying "user not found" vs "wrong password" separately on purpose
        # don't want to give hints about which part was wrong

        return create_access_token(
            user_id=user.id,
            username=user.username,
            # role is an enum column so user.role comes back as UserRole.ADMIN
            # need .value to get just "ADMIN" as a string for the jwt
            role=user.role.value,
        )