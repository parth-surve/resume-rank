from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class ScreeningStatusEnum(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ScreeningCreate(BaseModel):
    hackathon_id: int
    domain_id: int
    selection_limit: int
    waitlist_limit: int


class ScreeningOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hackathon_id: int
    domain_id: int
    selection_limit: int
    waitlist_limit: int

    status: ScreeningStatusEnum

    total_candidates: int
    processed_candidates: int
    failed_candidates: int

    started_at: datetime | None
    completed_at: datetime | None

    created_at: datetime
    updated_at: datetime


class ScreeningStartOut(BaseModel):
    screening_id: int
    status: ScreeningStatusEnum


class ScreeningResultItem(BaseModel):
    candidate_id: int
    name: str
    email: str
    final_score: int | None
    rank: int | None
    result_status: str
    processing_status: str


class PaginatedResults(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ScreeningResultItem]