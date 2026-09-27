import asyncio

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import SessionLocal, get_db
from app.schemas.screening import (
    ManualOverrideRequest,
    PaginatedResults,
    ScreeningCreate,
    ScreeningOut,
    ScreeningStartOut,
)
from app.services.screening_service import ScreeningService
from app.workflows.screening_workflow import run_screening
from app.deps import require_role


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
    response_model=ScreeningStartOut,
)
def start_screening(
    screening_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    result = ScreeningService(db).start(screening_id)

    def _run():
        bg_db = SessionLocal()
        try:
            asyncio.run(run_screening(screening_id, bg_db))
        finally:
            bg_db.close()

    background_tasks.add_task(_run)

    return result


@router.get(
    "/{screening_id}/results",
    response_model=PaginatedResults,
)
def get_screening_results(
    screening_id: int,
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return ScreeningService(db).get_results(
        screening_id,
        status_filter,
        page,
        page_size,
    )


@router.get(
    "/{screening_id}/failures",
)
def get_screening_failures(
    screening_id: int,
    db: Session = Depends(get_db),
):
    return ScreeningService(db).get_failures(screening_id)


@router.patch(
    "/{screening_id}/results/{result_id}/override",
)
def manual_override(
    screening_id: int,
    result_id: int,
    payload: ManualOverrideRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("ADMIN", "ORGANIZER", "SUPERADMIN")
    ),
):
    return ScreeningService(db).manual_override(
        screening_id=screening_id,
        result_id=result_id,
        new_status=payload.new_status,
        reason=payload.reason,
        user_id=current_user.id,
    )
