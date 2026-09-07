from fastapi import APIRouter, status,Depends
from sqlalchemy.orm import Session
from app.schemas.hackathon import HackathonOut, HackathonCreate
from app.services.hackathon_service import HackathonService
from app.db.database import get_db

router = APIRouter(prefix="/api/v1/hackathons", tags=["hackathons"])


@router.post("", response_model=HackathonOut,status_code=status.HTTP_201_CREATED)
def create_hackarthon(payload: HackathonCreate,db:Session = Depends(get_db) ):
    return HackathonService(db).create(payload)


@router.get("", response_model=list[HackathonOut])
def list_hackathons(db: Session = Depends(get_db)):
    return HackathonService(db).list()
