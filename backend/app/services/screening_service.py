from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models import Screening, ScreeningStatus, Candidate
from app.schemas.screening import ScreeningCreate, ScreeningStartOut
from app.db.models import Candidate
from app.schemas.screening import ScreeningResultItem, PaginatedResults
from app.schemas.candidate import FailureRecordOut

class ScreeningService:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, payload: ScreeningCreate) -> Screening:
        record = Screening(
            hackathon_id=payload.hackathon_id,
            domain_id=payload.domain_id,
            selection_limit=payload.selection_limit,
            waitlist_limit=payload.waitlist_limit,
            rubric_version=payload.rubric_version
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
    
    def get(self, screening_id:int)->Screening:
        record = self.db.query(Screening).filter(Screening.id == screening_id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screening not found")
        return record
    
    def list(self) -> list[Screening]:
        return self.db.query(Screening).all()
    
    
    def start(self, screening_id: int) -> ScreeningStartOut:
        screening = self.db.query(Screening).filter(Screening.id == screening_id).first()
        if not screening:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screening not found")

        if screening.status != ScreeningStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot start a screening with status {screening.status}",
            )

        candidate_count = self.db.query(Candidate).filter(
            Candidate.hackathon_id == screening.hackathon_id,
            Candidate.domain_id == screening.domain_id,
        ).count()
        if candidate_count == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No candidates found for this hackathon/domain")

        screening.status = ScreeningStatus.PROCESSING
        self.db.commit()
        self.db.refresh(screening)

        return ScreeningStartOut(screening_id=screening.id, status=screening.status)
    
    


    def get_results(
        self, screening_id: int, status_filter: str | None, page: int, page_size: int
    ) -> PaginatedResults:
        screening = self.get(screening_id)  # reuses your existing get(), which already 404s

        query = self.db.query(Candidate).filter(
            Candidate.hackathon_id == screening.hackathon_id,
            Candidate.domain_id == screening.domain_id,
        )

        if status_filter:
            query = query.filter(Candidate.final_decision == status_filter)

        total = query.count()

        candidates = (
            query.order_by(Candidate.rank.asc().nullslast())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        items = [
            ScreeningResultItem(
                candidate_id=c.id,
                name=c.name,
                email=c.email,
                final_score=c.final_score,
                rank=c.rank,
                final_decision=c.final_decision.value if c.final_decision else None,
                processing_status=c.processing_status.value,
            )
            for c in candidates
        ]

        return PaginatedResults(total=total, page=page, page_size=page_size, items=items)
    
    
    def get_failures(self, screening_id: int) -> list[Candidate]:
        screening = self.get(screening_id)
        candidates = self.db.query(Candidate).filter(
        Candidate.hackathon_id == screening.hackathon_id,
        Candidate.domain_id == screening.domain_id,
        Candidate.processing_status == "FAILED",
    ).all()

        return [
        FailureRecordOut(
            candidate_id=c.id,
            candidate_name=c.name,
            failure_stage=c.failure_stage or "unknown",
            failure_code=c.failure_code or "unknown",
            failure_reason=c.failure_reason or "",
            retry_count=c.retry_count,
        )
        for c in candidates
    ]