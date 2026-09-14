from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.hackathon import (
    HackathonCreate,
    HackathonOut,
    HackathonUpdate,
)
from app.services.hackathon_service import HackathonService


router = APIRouter(
    prefix="/api/v1/hackathons",
    tags=["hackathons"],
)


@router.post(
    "",
    response_model=HackathonOut,
    status_code=status.HTTP_201_CREATED,
)
def create_hackathon(
    payload: HackathonCreate,
    db: Session = Depends(get_db),
):
    return HackathonService(db).create(payload)


@router.get(
    "",
    response_model=list[HackathonOut],
)
def list_hackathons(
    db: Session = Depends(get_db),
):
    return HackathonService(db).list()


@router.get(
    "/{hackathon_id}",
    response_model=HackathonOut,
)
def get_hackathon(
    hackathon_id: int,
    db: Session = Depends(get_db),
):
    return HackathonService(db).get(hackathon_id)


@router.patch(
    "/{hackathon_id}",
    response_model=HackathonOut,
)
def update_hackathon(
    hackathon_id: int,
    payload: HackathonUpdate,
    db: Session = Depends(get_db),
):
    return HackathonService(db).update(hackathon_id, payload)


@router.delete(
    "/{hackathon_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_hackathon(
    hackathon_id: int,
    db: Session = Depends(get_db),
):
    HackathonService(db).delete(hackathon_id)