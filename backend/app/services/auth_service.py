from sqlalchemy.orm import Session

from app.db.models import User
from app.core.security import verify_password, create_access_token


class AuthService:
    """
    Handles authentication and user lookups.
    Routes should call this service instead of querying User directly.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_identifier(self, identifier: str) -> User | None:
        """
        Find a user by email.
        Email is the login identifier in our current User model.
        """
        return (
            self.db.query(User)
            .filter(User.email == identifier)
            .first()
        )

    def get_user_by_id(self, user_id: int) -> User | None:
        """
        Get a user from the ID stored in the JWT `sub` claim.
        """
        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    def authenticate(
        self,
        identifier: str,
        password: str,
    ) -> str | None:
        """
        Login flow:
        1. Find user by email
        2. Verify password
        3. Create JWT
        4. Return access token

        Returns None if authentication fails.
        """

        user = self.get_user_by_identifier(identifier)

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return create_access_token(
            user_id=user.id,
            role=user.role.value,
        )