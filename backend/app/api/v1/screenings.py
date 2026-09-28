import asyncio

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.db.database import SessionLocal, get_db
from app.db.models import ScreeningStatus
from app.schemas.screening import ScreeningCreate, ScreeningOut
from app.services.screening_service import ScreeningService
from app.workflows.screening_workflow import run_screening


def run_screening_background(screening_id: int) -> None:
    db = SessionLocal()

    try:
        asyncio.run(run_screening(screening_id, db))
    finally:
        db.close()


router = APIRouter(
    prefix="/api/v1/screenings",
    tags=["screenings"],
)


@router.post(
    "",
    response_model=ScreeningOut,
    status_code=status.HTTP_201_CREATED,
)
def create_screening(
    payload: ScreeningCreate,
    db: Session = Depends(get_db),
):
    return ScreeningService(db).create(payload)


@router.get(
    "",
    response_model=list[ScreeningOut],
)
def list_screenings(
    db: Session = Depends(get_db),
):
    return ScreeningService(db).list()


@router.get(
    "/{screening_id}",
    response_model=ScreeningOut,
)
def get_screening(
    screening_id: int,
    db: Session = Depends(get_db),
):
    return ScreeningService(db).get(screening_id)


@router.post(
    "/{screening_id}/start",
    response_model=ScreeningOut,
)
def start_screening(
    screening_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    screening = ScreeningService(db).get(screening_id)

    if screening.status != ScreeningStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Screening has already been started.",
        )

    screening.status = ScreeningStatus.IN_PROGRESS
    db.commit()
    db.refresh(screening)

    background_tasks.add_task(
        run_screening_background,
        screening_id,
    )

    return screening