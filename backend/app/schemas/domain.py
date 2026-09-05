from datetime import datetime
from pydantic import BaseModel, ConfigDict

class DomainCreate(BaseModel):
    name: str


class DomainUpdate(BaseModel):
    name: str | None = None
    
    
class DomainUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str 
    hackathon_id: int
    created_at: datetime 