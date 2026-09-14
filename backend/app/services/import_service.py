from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import Domain, Hackathon, Import
from app.schemas.imports import ImportCreate, ImportOut


class ImportService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: ImportCreate) -> ImportOut:
        hackathon = (
            self.db.query(Hackathon)
            .filter(Hackathon.id == payload.hackathon_id)
            .first()
        )

        if not hackathon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hackathon not found",
            )

        domain = (
            self.db.query(Domain)
            .filter(
                Domain.id == payload.domain_id,
                Domain.hackathon_id == payload.hackathon_id,
            )
            .first()
        )

        if not domain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain not found for this hackathon",
            )

        record = Import(
            hackathon_id=payload.hackathon_id,
            domain_id=payload.domain_id,
            filename=payload.filename,
            file_path=payload.file_path,
        )

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        return ImportOut.model_validate(record)

    def get(self, import_id: int) -> ImportOut:
        record = (
            self.db.query(Import)
            .filter(Import.id == import_id)
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Import not found",
            )

        return ImportOut.model_validate(record)

    def list(self, hackathon_id: int) -> list[ImportOut]:
        records = (
            self.db.query(Import)
            .filter(Import.hackathon_id == hackathon_id)
            .all()
        )

        return [ImportOut.model_validate(record) for record in records]