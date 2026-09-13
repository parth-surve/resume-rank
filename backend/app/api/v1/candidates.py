from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.candidate import CandidateOut
from app.services.candidate_service import CandidateService

router = APIRouter(prefix="/api/v1", tags=["candidates"])


@router.get("/candidates/{candidate_id}", response_model=CandidateOut)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    return CandidateService(db).get(candidate_id)


@router.get("/screenings/{screening_id}/candidates", response_model=list[CandidateOut])
def list_candidates_for_screening(screening_id: int, db: Session = Depends(get_db)):
    return CandidateService(db).list_for_screening(screening_id)

from app.schemas.candidate import CandidateOut

@router.post("/candidates/{candidate_id}/retry", response_model=CandidateOut)
def retry_candidate(candidate_id: int, db: Session = Depends(get_db)):
    return CandidateService(db).retry(candidate_id)