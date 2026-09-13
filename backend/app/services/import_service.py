import os 
import uuid
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status
from fastapi.responses import FileResponse

from app.db.models import Domain, Import

STORAGE_DIR = "./storage/uploads"

class ImportService:
    def __init__(self,db:Session):
        self.db = db
        
    async def upload_participants(
        self, hackathon_id: int, domain_id: int, file: UploadFile
    ) -> Import:
        domain = self.db.query(Domain).filter(Domain.id == domain_id, Domain.hackathon_id== hackathon_id).first()
        if not domain:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Domain not found for this hackathon")    
        
        if not file.filename.endswith((".xlsx", ".xls")):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="File must be .xlsx or .xls")
        
        os.makedirs(STORAGE_DIR, exist_ok=True)
        safe_name = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(STORAGE_DIR, safe_name)

        
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        record = Import(
            hackathon_id=hackathon_id,
            domain_id=domain_id,
            filename=file.filename,
            file_path=file_path,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
    def get_import_status(self, import_id: int) -> Import:
        record = self.db.query(Import).filter(Import.id == import_id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import not found")
        return record

def get_import_file(self, import_id: int) -> FileResponse:
    record = self.get_import_status(import_id)  # reuses the 404 check
    if not os.path.exists(record.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File no longer exists on disk")
    return FileResponse(path=record.file_path, filename=record.filename)