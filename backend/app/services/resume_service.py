from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import Candidate, Resume
from app.schemas.resume import ResumeCreate, ResumeOut


class ResumeService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: ResumeCreate) -> ResumeOut:
        candidate = (
            self.db.query(Candidate)
            .filter(Candidate.id == payload.candidate_id)
            .first()
        )

        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found",
            )

        resume = Resume(
            candidate_id=payload.candidate_id,
            resume_url=payload.resume_url,
            hashed_file=payload.hashed_file,
            file_type=payload.file_type,
            file_size=payload.file_size,
        )

        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)

        return ResumeOut.model_validate(resume)

    def get(self, resume_id: int) -> ResumeOut:
        resume = (
            self.db.query(Resume)
            .filter(Resume.id == resume_id)
            .first()
        )

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

        return ResumeOut.model_validate(resume)

    def list_by_candidate(
        self,
        candidate_id: int,
    ) -> list[ResumeOut]:
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

        resumes = (
            self.db.query(Resume)
            .filter(Resume.candidate_id == candidate_id)
            .order_by(Resume.id)
            .all()
        )

        return [
            ResumeOut.model_validate(resume)
            for resume in resumes
        ]