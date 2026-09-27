from sqlalchemy.orm import Session

from ai.evaluator import evaluate_candidate
from ai.rubric import RUBRIC
from data_pipeline.resume_downloader import download_resume_in_memory

from app.db.models import (
    Candidate,
    CandidateProcessing,
    CandidateProcessingStatus,
    Domain,
    Evaluation,
    ProcessingFailure,
    ProcessingStage,
    Resume,
    Screening,
    ScreeningResult,
    ScreeningResultStatus,
    ScreeningStatus,
)


async def run_screening(
    screening_id: int,
    db: Session,
) -> None:
    """
    Run the complete V1 screening workflow.

    Flow:
        Screening
        -> CandidateProcessing
        -> Resume download + text extraction
        -> AI evaluation
        -> Evaluation
        -> Ranking
        -> ScreeningResult
    """

    screening = (
        db.query(Screening)
        .filter(Screening.id == screening_id)
        .first()
    )

    if not screening:
        return

    try:
        # ---------------------------------------------------------
        # 1. Get domain requirements
        # ---------------------------------------------------------

        domain = (
            db.query(Domain)
            .filter(Domain.id == screening.domain_id)
            .first()
        )

        if not domain:
            raise ValueError("Screening domain not found.")

        domain_requirements = (
            domain.description
            if domain.description
            else domain.name
        )

        # ---------------------------------------------------------
        # 2. Get candidate processing records
        # ---------------------------------------------------------

        processing_records = (
            db.query(CandidateProcessing)
            .filter(
                CandidateProcessing.screening_id == screening.id,
                CandidateProcessing.status
                == CandidateProcessingStatus.PENDING,
            )
            .all()
        )

        if not processing_records:
            screening.status = ScreeningStatus.COMPLETED
            screening.total_candidates = 0
            screening.processed_candidates = 0
            screening.failed_candidates = 0
            db.commit()
            return

        screening.total_candidates = len(processing_records)
        screening.status = ScreeningStatus.IN_PROGRESS
        db.commit()

        # ---------------------------------------------------------
        # 3. Process each candidate
        # ---------------------------------------------------------

        for processing in processing_records:

            try:
                processing.status = CandidateProcessingStatus.PROCESSING
                db.commit()

                candidate = (
                    db.query(Candidate)
                    .filter(Candidate.id == processing.candidate_id)
                    .first()
                )

                if not candidate:
                    raise ValueError(
                        f"Candidate {processing.candidate_id} not found."
                    )

                # -------------------------------------------------
                # 4. Get candidate resume
                # -------------------------------------------------

                resume = (
                    db.query(Resume)
                    .filter(Resume.candidate_id == candidate.id)
                    .order_by(Resume.id.desc())
                    .first()
                )

                if not resume:
                    raise ValueError(
                        f"No resume found for candidate {candidate.id}."
                    )

                # -------------------------------------------------
                # 5. Download resume + extract text
                # -------------------------------------------------

                download_result = download_resume_in_memory(
                    resume.resume_url
                )

                if not download_result.get("success"):
                    raise ValueError(
                        download_result.get(
                            "reason",
                            "Resume processing failed.",
                        )
                    )

                resume_text = download_result.get("resume_text", "").strip()

                if not resume_text:
                    raise ValueError(
                        "Resume text extraction returned empty text."
                    )

                # -------------------------------------------------
                # 6. Run AI evaluator
                # -------------------------------------------------

                ai_result = evaluate_candidate(
                    resume_text=resume_text,
                    rubric=str(RUBRIC),
                    domain_requirements=domain_requirements,
                    prompt_version="v1",
                    provider="groq",
                )

                evaluation_model = ai_result["evaluation"]
                scores = ai_result["scores"]

                # -------------------------------------------------
                # 7. Save Evaluation
                # -------------------------------------------------

                evaluation = Evaluation(
                    candidate_processing_id=processing.id,
                    model="groq",
                    prompt_version="v1",
                    rubric_version="v1",
                    evaluation_data=evaluation_model.model_dump(
                        mode="json"
                    ),
                    technical_score=scores["technical_skills"],
                    competitive_score=scores[
                        "competitive_achievement"
                    ],
                    relevant_experience_score=scores[
                        "relevant_experience"
                    ],
                    projects_score=scores["projects"],
                    potential_score=scores[
                        "demonstrated_potential"
                    ],
                    domain_relevance_score=scores[
                        "domain_relevance"
                    ],
                    final_score=scores["total_score"],
                )

                db.add(evaluation)
                db.flush()

                # -------------------------------------------------
                # 8. Save ScreeningResult
                # -------------------------------------------------

                screening_result = ScreeningResult(
                    screening_id=screening.id,
                    candidate_processing_id=processing.id,
                    evaluation_id=evaluation.id,
                    final_score=scores["total_score"],
                    result_status=ScreeningResultStatus.PENDING,
                )

                db.add(screening_result)

                # -------------------------------------------------
                # 9. Mark candidate processing completed
                # -------------------------------------------------

                processing.status = CandidateProcessingStatus.COMPLETED

                db.commit()

            except Exception as candidate_error:
                db.rollback()

                # Re-fetch processing record after rollback
                processing = (
                    db.query(CandidateProcessing)
                    .filter(
                        CandidateProcessing.id == processing.id
                    )
                    .first()
                )

                if not processing:
                    continue

                processing.status = CandidateProcessingStatus.FAILED
                processing.retry_count += 1

                failure = ProcessingFailure(
                    candidate_processing_id=processing.id,
                    stage=ProcessingStage.EVALUATION,
                    error_code="SCREENING_PROCESSING_ERROR",
                    error_message=str(candidate_error),
                    retry_count=processing.retry_count,
                )

                db.add(failure)
                db.commit()

        # ---------------------------------------------------------
        # 10. Rank successfully evaluated candidates
        # ---------------------------------------------------------

        results = (
            db.query(ScreeningResult)
            .filter(
                ScreeningResult.screening_id == screening.id
            )
            .order_by(
                ScreeningResult.final_score.desc(),
                ScreeningResult.id.asc(),
            )
            .all()
        )

        for rank, result in enumerate(results, start=1):
            result.rank = rank

            if rank <= screening.selection_limit:
                result.result_status = ScreeningResultStatus.SELECTED

            elif rank <= (
                screening.selection_limit
                + screening.waitlist_limit
            ):
                result.result_status = ScreeningResultStatus.WAITLISTED

            else:
                result.result_status = ScreeningResultStatus.REJECTED

        # ---------------------------------------------------------
        # 11. Update screening counters
        # ---------------------------------------------------------

        processed_count = (
            db.query(CandidateProcessing)
            .filter(
                CandidateProcessing.screening_id == screening.id,
                CandidateProcessing.status
                == CandidateProcessingStatus.COMPLETED,
            )
            .count()
        )

        failed_count = (
            db.query(CandidateProcessing)
            .filter(
                CandidateProcessing.screening_id == screening.id,
                CandidateProcessing.status
                == CandidateProcessingStatus.FAILED,
            )
            .count()
        )

        screening.processed_candidates = processed_count
        screening.failed_candidates = failed_count

        if failed_count > 0 and processed_count == 0:
            screening.status = ScreeningStatus.FAILED
        else:
            screening.status = ScreeningStatus.COMPLETED

        db.commit()

    except Exception as workflow_error:
        db.rollback()

        screening = (
            db.query(Screening)
            .filter(Screening.id == screening_id)
            .first()
        )

        if screening:
            screening.status = ScreeningStatus.FAILED
            db.commit()

        raise workflow_error