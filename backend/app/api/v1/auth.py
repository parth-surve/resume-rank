from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db          # need to confirm exact path w/ db member
from app.schemas.auth import LoginRequest, TokenResponse, UserOut
from app.services.auth_service import AuthService
from app.deps import get_current_user        # writing this file next

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # payload = whatever the client sent (identifier + password)
    # just hand it off to the service, don't do logic here

    token = AuthService(db).authenticate(payload.identifier, payload.password)

    if not token:
        # same error for wrong username/email AND wrong password
        # not revealing which one was wrong
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
        )

    return TokenResponse(access_token=token)

@router.get("/me", response_model=UserOut)
def read_current_user(current_user = Depends(get_current_user)):
    # get_current_user already verified the jwt + fetched the user
    # just return it, response_model handles converting to UserOut
    return current_user