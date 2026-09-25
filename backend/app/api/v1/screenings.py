from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.screening import ScreeningCreate, ScreeningOut
from app.services.screening_service import ScreeningService


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