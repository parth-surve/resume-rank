from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.resume import ResumeCreate, ResumeOut
from app.services.resume_service import ResumeService


router = APIRouter(
    prefix="/api/v1/resumes",
    tags=["resumes"],
)


@router.post(
    "",
    response_model=ResumeOut,
    status_code=status.HTTP_201_CREATED,
)
def create_resume(
    payload: ResumeCreate,
    db: Session = Depends(get_db),
):
    return ResumeService(db).create(payload)


@router.get(
    "/{resume_id}",
    response_model=ResumeOut,
)
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
):
    return ResumeService(db).get(resume_id)


@router.get(
    "/candidate/{candidate_id}",
    response_model=list[ResumeOut],
)
def list_candidate_resumes(
    candidate_id: int,
    db: Session = Depends(get_db),
):
    return ResumeService(db).list_by_candidate(candidate_id)