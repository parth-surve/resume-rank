from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.db.models import ScreeningStatus


class ScreeningCreate(BaseModel):
    hackathon_master_id: UUID
    domain_master_id: UUID
    selection_limit: int
    waitlist_limit: int


class ScreeningOut(BaseModel):
    id: int
    hackathon_master_id: UUID
    domain_master_id: UUID
    status: ScreeningStatus
    total_candidate: int
    processed_candidate: int
    failed_candidates: int
    selection_limit: int
    waitlist_limit: int
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)