from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ImportCreate(BaseModel):
    hackathon_id: int
    domain_id: int
    filename: str
    file_path: str


class ImportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hackathon_id: int
    domain_id: int
    filename: str
    file_path: str
    created_at: datetime