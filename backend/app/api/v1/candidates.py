from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.candidate import CandidateCreate, CandidateOut
from app.services.candidate_service import CandidateService


router = APIRouter(
    prefix="/api/v1/candidates",
    tags=["candidates"],
)


@router.post(
    "",
    response_model=CandidateOut,
    status_code=status.HTTP_201_CREATED,
)
def create_candidate(
    payload: CandidateCreate,
    db: Session = Depends(get_db),
):
    return CandidateService(db).create(payload)


@router.get(
    "/{candidate_id}",
    response_model=CandidateOut,
)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
):
    return CandidateService(db).get(candidate_id)


@router.get(
    "",
    response_model=list[CandidateOut],
)
def list_candidates(
    db: Session = Depends(get_db),
):
    return CandidateService(db).list()