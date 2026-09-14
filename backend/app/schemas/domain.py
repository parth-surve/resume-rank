from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DomainCreate(BaseModel):
    name: str
    description: str | None = None


class DomainUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class DomainOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    hackathon_id: int
    created_at: datetime
    updated_at: datetime