from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class CandidateCreate(BaseModel):
    name: str
    email: EmailStr
    mobile: str | None = None
    college: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None


class CandidateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    mobile: str | None = None
    college: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    created_at: datetime
    updated_at: datetime