from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr


class ProcessingStatusEnum(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class FinalDecisionEnum(str, Enum):
    SELECTED = "SELECTED"
    WAITLIST = "WAITLIST"
    REJECTED = "REJECTED"


class CandidateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    hackathon_id: int
    domain_id: int
    name: str
    email: EmailStr
    college: str | None = None
    resume_url: str | None = None
    github: str | None = None
    linkedin: str | None = None
    processing_status: ProcessingStatusEnum
    final_decision: FinalDecisionEnum | None = None
    final_score: float | None = None
    rank: int | None = None
    created_at: datetime


class FailureRecordOut(BaseModel):
    candidate_id: int
    candidate_name: str
    failure_stage: str
    failure_code: str
    failure_reason: str
    retry_count: int