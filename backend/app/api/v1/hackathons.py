from fastapi import APIRouter, status
from sqlalchemy.orm import Session
from app.schemas.hackathon import HackathonOut, HackathonCreate
from app.services.hackathon_service import HackathonService

router = APIRouter(prefix="/api/v1/hackathons", tags=["hackathons"])
service = HackathonService()


@router.post("", response_model=HackathonOut,status_code=status.HTTP_201_CREATED)
def create_hackarthon(payload: HackathonCreate, ):
    return service.create(payload)


@router.get("", response_model=list[HackathonOut])
def list_hackathons():
    return service.list()
