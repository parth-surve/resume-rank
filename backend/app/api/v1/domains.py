from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.domain import DomainCreate, DomainUpdate, DomainOut
from app.services.domain_service import DomainServices


# Nested under a hackathon: /api/v1/hackathons/{hackathon_id}/domains

nested_router = APIRouter(prefix="/api/v1/hackathons", tags=["domains"])

@nested_router.post("/{hackathon_id}/domains", response_model=DomainOut, status_code=status.HTTP_201_CREATED)
def create_domain(hackathon_id:int, payload:DomainCreate,db:Session = Depends(get_db)):
    return DomainServices(db).create(hackathon_id,payload)

@nested_router.get("/{hackathon_id}/domains",response_model=list[DomainOut])
def list_domains(hackathon_id:int, db:Session = Depends(get_db)):
    return DomainServices(db).list(hackathon_id)



router = APIRouter(prefix="/api/v1/domains", tags=["domains"])

@router.get("/{domain_id}", response_model=DomainOut)
def get_domain(domain_id:int, db:Session = Depends(get_db)):
    return DomainServices(db).get(domain_id)

@router.patch("/{domain_id}", response_model=DomainOut)
def update_domain(domain_id:int, payload:DomainUpdate,db:Session = Depends(get_db)):
    return DomainServices(db).update(domain_id,payload)


@router.delete("/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_domain(domain_id: int, db: Session = Depends(get_db)):
    DomainServices(db).delete(domain_id)