from datetime import datetime
from app.schemas.hackathon import HackathonCreate, HackathonOut

# Fake in-memory "database" just so we have something to work with

_fake_db: list[dict] = []        # change when the Dataset is ready
_next_id = 1


class HackathonService:
    def create(self, payload: HackathonCreate) -> HackathonOut:
        global _next_id     # to take id from global
        record = {
            "id": _next_id,
            "name": payload.name,
            "description": payload.description,
            "created_at": datetime.utcnow()
        }
        
        _fake_db.append(record)
        _next_id += 1
        return HackathonOut(**record)  # unpacks the dictionary so the dictionary keys become function argument 
    
    def list(self) -> list[HackathonOut]:
        return [HackathonOut(**r) for r in _fake_db ]