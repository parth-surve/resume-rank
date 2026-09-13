import asyncio
from sqlalchemy.orm import Session

from app.db.models import Screening, ScreeningStatus, Candidate, ProcessingStatus


async def run_screening(screening_id: int, db: Session):
    screening = db.query(Screening).filter(Screening.id == screening_id).first()
    if not screening:
        return

    candidates = db.query(Candidate).filter(
        Candidate.hackathon_id == screening.hackathon_id,
        Candidate.domain_id == screening.domain_id,
    ).all()

    screening.total = len(candidates)
    db.commit()

    for candidate in candidates:
        # TEMP: fake processing delay instead of real resume download + AI eval
        await asyncio.sleep(1)

        candidate.processing_status = ProcessingStatus.COMPLETED
        screening.processed += 1
        screening.successful += 1
        db.commit()

    screening.status = ScreeningStatus.COMPLETED
    db.commit()