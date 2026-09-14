from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.imports import ImportCreate, ImportOut
from app.services.import_service import ImportService


router = APIRouter(
    prefix="/api/v1/imports",
    tags=["imports"],
)


@router.post(
    "",
    response_model=ImportOut,
    status_code=status.HTTP_201_CREATED,
)
def create_import(
    payload: ImportCreate,
    db: Session = Depends(get_db),
):
    return ImportService(db).create(payload)


@router.get(
    "/{import_id}",
    response_model=ImportOut,
)
def get_import(
    import_id: int,
    db: Session = Depends(get_db),
):
    return ImportService(db).get(import_id)


@router.get(
    "/hackathons/{hackathon_id}",
    response_model=list[ImportOut],
)
def list_imports(
    hackathon_id: int,
    db: Session = Depends(get_db),
):
    return ImportService(db).list(hackathon_id)