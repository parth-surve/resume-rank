from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import Candidate
from app.schemas.candidate import CandidateCreate, CandidateOut


class CandidateService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: CandidateCreate) -> CandidateOut:
        existing_candidate = (
            self.db.query(Candidate)
            .filter(Candidate.email == payload.email)
            .first()
        )

        if existing_candidate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Candidate with this email already exists",
            )

        candidate = Candidate(
            name=payload.name,
            email=payload.email,
            mobile=payload.mobile,
            college=payload.college,
            linkedin_url=payload.linkedin_url,
            github_url=payload.github_url,
        )

        self.db.add(candidate)
        self.db.commit()
        self.db.refresh(candidate)

        return CandidateOut.model_validate(candidate)

    def get(self, candidate_id: int) -> CandidateOut:
        candidate = (
            self.db.query(Candidate)
            .filter(Candidate.id == candidate_id)
            .first()
        )

        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found",
            )

        return CandidateOut.model_validate(candidate)

    def list(self) -> list[CandidateOut]:
        candidates = (
            self.db.query(Candidate)
            .order_by(Candidate.id)
            .all()
        )

        return [
            CandidateOut.model_validate(candidate)
            for candidate in candidates
        ]