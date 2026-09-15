from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """
    What the client sends to POST /api/v1/auth/login
    identifier = username OR email, backend figures out which
    """
    identifier: str
    password: str


class TokenResponse(BaseModel):
    """
    What the backend sends back after a successful login
    """
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    """
    What the backend sends back for GET /api/v1/auth/me
    Never include hashed_password here — this is what gets
    shown to the frontend/client, so no sensitive fields.
    """
    id: int
    username: str
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True