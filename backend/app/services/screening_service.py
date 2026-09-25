from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import Domain, Hackathon, HackathonDomain, Screening
from app.schemas.screening import ScreeningCreate


class ScreeningService:

    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: ScreeningCreate) -> Screening:
        hackathon = (
            self.db.query(Hackathon)
            .filter(Hackathon.id == payload.hackathon_master_id)
            .first()
        )

        if not hackathon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hackathon not found",
            )

        domain = (
            self.db.query(Domain)
            .filter(Domain.id == payload.domain_master_id)
            .first()
        )

        if not domain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain not found",
            )

        relationship = (
            self.db.query(HackathonDomain)
            .filter(
                HackathonDomain.hackathon_id == payload.hackathon_master_id,
                HackathonDomain.domain_id == payload.domain_master_id,
            )
            .first()
        )

        if not relationship:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Domain does not belong to the selected hackathon",
            )

        if payload.selection_limit < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="selection_limit cannot be negative",
            )

        if payload.waitlist_limit < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="waitlist_limit cannot be negative",
            )

        screening = Screening(
            hackathon_master_id=payload.hackathon_master_id,
            domain_master_id=payload.domain_master_id,
            selection_limit=payload.selection_limit,
            waitlist_limit=payload.waitlist_limit,
        )

        self.db.add(screening)
        self.db.commit()
        self.db.refresh(screening)

        return screening

    def get(self, screening_id: int) -> Screening:
        screening = (
            self.db.query(Screening)
            .filter(Screening.id == screening_id)
            .first()
        )

        if not screening:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Screening not found",
            )

        return screening

    def list(self) -> list[Screening]:
        return self.db.query(Screening).all()