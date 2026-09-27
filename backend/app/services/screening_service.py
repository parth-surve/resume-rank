import logging
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
    ManualOverride,
)
from app.schemas.screening import (
    PaginatedResults,
    ScreeningCreate,
    ScreeningResultItem,
    ScreeningStartOut,
)
from app.core.metrics import SCREENING_STARTS

logger = logging.getLogger(__name__)

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
            logger.warning(
                "Screening start failed: screening_id=%s reason=no_candidates",
                screening_id,
            )
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
        SCREENING_STARTS.inc()

        logger.info(
            "Screening started: screening_id=%s total_candidates=%s",
            screening.id,
            screening.total_candidates,
        )

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

    def manual_override(
        self,
        screening_id: int,
        result_id: int,
        new_status: ScreeningResultStatus,
        reason: str,
        user_id: int,
    ) -> ScreeningResult:
        screening = self.get(screening_id)

        result = (
            self.db.query(ScreeningResult)
            .filter(
                ScreeningResult.id == result_id,
                ScreeningResult.screening_id == screening.id,
            )
            .first()
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Screening result not found",
            )

        if not reason.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Override reason is required",
            )

        previous_status = result.result_status

        if previous_status == new_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New status must be different from the current status",
            )

        result.result_status = new_status

        override = ManualOverride(
            screening_result_id=result.id,
            previous_status=previous_status,
            new_status=new_status,
            reason=reason.strip(),
            overridden_by=user_id,
        )

        self.db.add(override)
        self.db.commit()
        self.db.refresh(result)

        logger.info(
            "Manual override completed: screening_id=%s result_id=%s "
            "previous_status=%s new_status=%s overridden_by=%s",
            screening_id,
            result_id,
            previous_status.value,
            new_status.value,
            user_id,
        )

        return result

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
