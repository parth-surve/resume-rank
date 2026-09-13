from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.database import get_db,SessionLocal
from app.schemas.screening import ScreeningCreate, ScreeningOut, ScreeningStartOut,PaginatedResults
from app.services.screening_service import ScreeningService
from app.workflows.screening_workflow import run_screening
from fastapi import Query

router = APIRouter(prefix="/api/v1/screenings", tags=["screenings"])


@router.post("", response_model=ScreeningOut, status_code=status.HTTP_201_CREATED)
def create_screening(payload: ScreeningCreate, db: Session = Depends(get_db)):
    return ScreeningService(db).create(payload)


@router.get("", response_model=list[ScreeningOut])
def list_screenings(db: Session = Depends(get_db)):
    return ScreeningService(db).list()


@router.get("/{screening_id}", response_model=ScreeningOut)
def get_screening(screening_id: int, db: Session = Depends(get_db)):
    return ScreeningService(db).get(screening_id)


@router.post("/{screening_id}/start", response_model=ScreeningStartOut)
def start_screening(screening_id: int, db: Session = Depends(get_db)):
    return ScreeningService(db).start(screening_id)

@router.post("/{screening_id}/start", response_model=ScreeningStartOut)
def start_screening(
    screening_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    result = ScreeningService(db).start(screening_id)

    # IMPORTANT: the background task needs its OWN db session, not the
    # request's session — the request's session closes right after this
    # function returns, but the background task keeps running after that.
    def _run():
        bg_db = SessionLocal()
        try:
            import asyncio
            asyncio.run(run_screening(screening_id, bg_db))
        finally:
            bg_db.close()

    background_tasks.add_task(_run)
    return result



@router.get("/{screening_id}/results", response_model=PaginatedResults)
def get_screening_results(
    screening_id: int,
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return ScreeningService(db).get_results(screening_id, status, page, page_size)


@router.get("/{screening_id}/failures")
def get_screening_failures(screening_id: int, db: Session = Depends(get_db)):
    return ScreeningService(db).get_failures(screening_id)