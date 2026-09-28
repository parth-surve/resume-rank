from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.db.models import (
    CandidateMaster,
    CandidateProcessing,
    Domain,
    Hackathon,
    HackathonDomain,
    Screening,
    Team,
    TeamMember,
)
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

    def prepare_candidates(self, screening_id: int) -> list[CandidateProcessing]:
        screening = self.get(screening_id)

        candidates = (
            self.db.query(
                CandidateMaster.id,
                Team.id.label("team_id"),
            )
            .join(
                TeamMember,
                TeamMember.candidate_id == CandidateMaster.id,
            )
            .join(
                Team,
                Team.id == TeamMember.team_id,
            )
            .filter(
                Team.hackathon_id == screening.hackathon_master_id,
                Team.domain_id == screening.domain_master_id,
            )
            .order_by(Team.id.asc(), CandidateMaster.id.asc())
            .all()
        )

        processing_records = []
        seen_candidate_ids = set()

        for candidate_id, team_id in candidates:
            if candidate_id in seen_candidate_ids:
                continue

            seen_candidate_ids.add(candidate_id)

            existing = (
                self.db.query(CandidateProcessing)
                .filter(
                    CandidateProcessing.screening_id == screening_id,
                    CandidateProcessing.candidate_master_id == candidate_id,
                )
                .first()
            )

            if existing:
                processing_records.append(existing)
                continue

            processing = CandidateProcessing(
                screening_id=screening_id,
                candidate_master_id=candidate_id,
                team_id=team_id,
            )

            self.db.add(processing)
            processing_records.append(processing)

        screening.total_candidate = len(processing_records)

        self.db.commit()

        for processing in processing_records:
            self.db.refresh(processing)

        return processing_records
