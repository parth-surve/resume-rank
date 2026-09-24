from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.db.models import ExtractionStatus


class ResumeCreate(BaseModel):
    candidate_id: int
    resume_url: str
    hashed_file: str | None = None
    file_type: str
    file_size: int


class ResumeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    candidate_id: int
    resume_url: str
    hashed_file: str | None = None
    file_type: str
    file_size: int
    extraction_status: ExtractionStatus
    created_at: datetime
    updated_at: datetime