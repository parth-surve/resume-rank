from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.imports import ImportOut
from app.services.import_service import ImportService

router = APIRouter(prefix="/api/v1", tags=["imports"])


@router.post("/hackathons/{hackarhon_id}/domains/{domain_id}/participants/upload",
             response_class=ImportOut,
             status_code=status.HTTP_400_BAD_REQUEST
             )
async def upload_participants(
    hackathon_id: int,
    domain_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
     return await ImportService(db).upload_participants(hackathon_id, domain_id, file)
 
router.get("/imports/{import_id}", response_model=ImportOut)
def get_import_status(import_id: int, db: Session = Depends(get_db)):
    return ImportService(db).get_import_status(import_id)


@router.get("/imports/{import_id}/file")
def get_import_file(import_id: int, db: Session = Depends(get_db)):
    return ImportService(db).get_import_file(import_id)