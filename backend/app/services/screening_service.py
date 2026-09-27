from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.models import (
    Candidate,
    CandidateProcessing,
    ProcessingFailure,
    Screening,
    ScreeningResult,
    ScreeningResultStatus,
    ScreeningStatus,
    Team,
    TeamMember,
)
from app.schemas.screening import (
    PaginatedResults,
    ScreeningCreate,
    ScreeningResultItem,
    ScreeningStartOut,
)


class ScreeningService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: ScreeningCreate) -> Screening:
        record = Screening(
            hackathon_id=payload.hackathon_id,
            domain_id=payload.domain_id,
            selection_limit=payload.selection_limit,
            waitlist_limit=payload.waitlist_limit,
        )

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        return record

    def get(self, screening_id: int) -> Screening:
        record = (
            self.db.query(Screening)
            .filter(Screening.id == screening_id)
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Screening not found",
            )

        return record

    def list(self) -> List[Screening]:
        return (
            self.db.query(Screening)
            .order_by(Screening.id.desc())
            .all()
        )

    def start(self, screening_id: int) -> ScreeningStartOut:
        screening = self.get(screening_id)

        if screening.status != ScreeningStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot start a screening with status "
                    f"{screening.status.value}"
                ),
            )

        candidate_ids = (
            self.db.query(TeamMember.candidate_id)
            .join(Team, Team.id == TeamMember.team_id)
            .filter(
                Team.hackathon_id == screening.hackathon_id,
                Team.domain_id == screening.domain_id,
            )
            .distinct()
            .all()
        )

        candidate_ids = [candidate_id for (candidate_id,) in candidate_ids]

        if not candidate_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No candidates found for this hackathon/domain",
            )

        existing_candidate_ids = {
            candidate_id
            for (candidate_id,) in (
                self.db.query(CandidateProcessing.candidate_id)
                .filter(
                    CandidateProcessing.screening_id == screening.id
                )
                .all()
            )
        }

        for candidate_id in candidate_ids:
            if candidate_id in existing_candidate_ids:
                continue

            self.db.add(
                CandidateProcessing(
                    screening_id=screening.id,
                    candidate_id=candidate_id,
                )
            )

        screening.status = ScreeningStatus.IN_PROGRESS
        screening.total_candidates = len(candidate_ids)
        screening.processed_candidates = 0
        screening.failed_candidates = 0

        self.db.commit()
        self.db.refresh(screening)

        return ScreeningStartOut(
            screening_id=screening.id,
            status=screening.status,
        )

    def get_results(
        self,
        screening_id: int,
        status_filter: str | None,
        page: int,
        page_size: int,
    ) -> PaginatedResults:
        screening = self.get(screening_id)

        query = (
            self.db.query(
                ScreeningResult,
                CandidateProcessing,
                Candidate,
            )
            .join(
                CandidateProcessing,
                CandidateProcessing.id
                == ScreeningResult.candidate_processing_id,
            )
            .join(
                Candidate,
                Candidate.id == CandidateProcessing.candidate_id,
            )
            .filter(
                ScreeningResult.screening_id == screening.id
            )
        )

        if status_filter:
            query = query.filter(
                ScreeningResult.result_status == status_filter
            )

        total = query.count()

        rows = (
            query
            .order_by(ScreeningResult.rank.asc().nullslast())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        items = [
            ScreeningResultItem(
                candidate_id=candidate.id,
                name=candidate.name,
                email=str(candidate.email),
                final_score=result.final_score,
                rank=result.rank,
                result_status=result.result_status.value,
                processing_status=processing.status.value,
            )
            for result, processing, candidate in rows
        ]

        return PaginatedResults(
            total=total,
            page=page,
            page_size=page_size,
            items=items,
        )

    def get_failures(self, screening_id: int) -> List[ProcessingFailure]:
        self.get(screening_id)

        return (
            self.db.query(ProcessingFailure)
            .join(
                CandidateProcessing,
                CandidateProcessing.id
                == ProcessingFailure.candidate_processing_id,
            )
            .filter(
                CandidateProcessing.screening_id == screening_id
            )
            .order_by(ProcessingFailure.failed_at.desc())
            .all()
        )