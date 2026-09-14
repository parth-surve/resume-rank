from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HackathonCreate(BaseModel):
    name: str
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class HackathonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    created_at: datetime
    updated_at: datetime


class HackathonUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None