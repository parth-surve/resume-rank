from datetime import datetime
from pydantic  import BaseModel, ConfigDict


class HackathonCreate(BaseModel):
    name: str
    description: str|None = None
    
class HackathonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str | None = None
    created_at: datetime