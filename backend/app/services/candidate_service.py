from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models import Candidate,ProcessingStatus


class CandidateService:
    def __init__(self, db: Session):
        self.db = db

    def get(self, candidate_id: int) -> Candidate:
        record = self.db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
        return record

    def list_for_screening(self, screening_id: int) -> list[Candidate]:
        from app.db.models import Screening

        screening = self.db.query(Screening).filter(Screening.id == screening_id).first()
        if not screening:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screening not found")

        return self.db.query(Candidate).filter(
            Candidate.hackathon_id == screening.hackathon_id,
            Candidate.domain_id == screening.domain_id,
        ).all()
        
    def retry(self, candidate_id: int) -> Candidate:
        candidate = self.get(candidate_id)  # reuses existing 404 check

        if candidate.processing_status != ProcessingStatus.FAILED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot retry a candidate with status {candidate.processing_status}",
            )

        candidate.processing_status = ProcessingStatus.PENDING
        candidate.retry_count += 1
        candidate.failure_stage = None
        candidate.failure_code = None
        candidate.failure_reason = None
        self.db.commit()
        self.db.refresh(candidate)
        return candidate