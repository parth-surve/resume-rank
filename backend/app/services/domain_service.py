from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models import Domain, Hackathon
from app.schemas.domain import DomainCreate, DomainUpdate, DomainOut



class DomainServices:
    def __init__(self, db:Session):
        self.db = db
    
    def create(self,hackathon_id: int, playload:DomainCreate)-> DomainOut:
        hackathon = self.db.quary(Hackathon).filter(Hackathon.id == hackathon_id).first()
        
        if not hackathon:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
        
        record = Domain(name = playload.name, hackathon_id=hackathon_id)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return DomainOut.model_validate(record)

    def list(self, hackathon_id: int) -> list[DomainOut]:
        records = self.db.query(Domain).filter(Domain.hackathon_id == hackathon_id).all()
        return [DomainOut.model_validate(r) for r in records]
    
    def get(self, domain_id:int) -> DomainOut:
        record = self.db.query(Domain).filter(Domain.id == domain_id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="status not found")
        return DomainOut.model_validate(record)

    def update(self, domain_id:int, payload: DomainUpdate)->DomainOut:
        record = self.db.query(Domain).filter(Domain.id == domain_id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,  detail="status not found")
        update_data = payload.model_dump(exclude_unset=True)
        for field,value in update_data.item():
            setattr(record,field,value)
        
        self.db.commit()
        self.db.refresh(record)
        return DomainOut.model_validate(record)
    
    def delete(self, domain_id:int) ->None:
        record = self.db.query(Domain).filter(Domain.id == domain_id).first()
        
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="status not found")
        self.db.delete(record)
        self.db.commit()