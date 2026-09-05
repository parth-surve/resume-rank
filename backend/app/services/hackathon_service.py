from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models import Hackathon
from app.schemas.hackathon import HackathonCreate, HackathonUpdate, HackathonOut


class HackathonService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: HackathonCreate) -> HackathonOut:
        record = Hackathon(
            name=payload.name,
            description=payload.description,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return HackathonOut.model_validate(record)

    def list(self) -> list[HackathonOut]:
        records = self.db.query(Hackathon).all()
        return [HackathonOut.model_validate(r) for r in records]

    def get(self, hackathon_id: int) -> HackathonOut:
        record = self.db.query(Hackathon).filter(Hackathon.id == hackathon_id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
        return HackathonOut.model_validate(record)

    def update(self, hackathon_id: int, payload: HackathonUpdate) -> HackathonOut:
        record = self.db.query(Hackathon).filter(Hackathon.id == hackathon_id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(record, field, value)

        self.db.commit()
        self.db.refresh(record)
        return HackathonOut.model_validate(record)

    def delete(self, hackathon_id: int) -> None:
        record = self.db.query(Hackathon).filter(Hackathon.id == hackathon_id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
        self.db.delete(record)
        self.db.commit()