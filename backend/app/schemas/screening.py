from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict

class ScreeningStatusEnum(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ScreeningCreate(BaseModel):
    hackathon_id: int
    domain_id: int
    selection_limit: int
    waitlist_limit: int
    rubric_version: str
    
class ScreeningOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    hackathon_id: int
    domain_id: int
    selection_limit: int
    waitlist_limit: int
    rubric_version: str
    status: ScreeningStatusEnum
    created_at: datetime
    
    
class ScreeningStartOut(BaseModel):
    screening_id: int
    status: ScreeningStatusEnum
    
class ScreeningResultItem(BaseModel):
    candidate_id: int
    name: str
    email: str
    final_score: float | None
    rank: int | None
    final_decision: str | None
    processing_status: str


class PaginatedResults(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ScreeningResultItem]