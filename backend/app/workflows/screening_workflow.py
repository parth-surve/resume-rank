import logging
from datetime import datetime, timezone
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

logger = logging.getLogger(__name__)


def run_screening(
    screening_id: int,
    db: Session,
) -> None:
    """
    Run the complete screening workflow.

    Flow:
        Screening
        -> CandidateProcessing (Pending / Interrupted)
        -> Resume download + text extraction (EXTRACTION stage)
        -> AI evaluation (EVALUATION stage)
        -> Evaluation & ScreeningResult persistence (SCORING stage)
        -> Deterministic Ranking
        -> Final Screening Status & Counters
    """

    screening = (
        db.query(Screening)
        .filter(Screening.id == screening_id)
        .first()
    )

    if not screening:
        logger.warning("Screening %s not found for processing", screening_id)
        return

    try:
        if screening.started_at is None:
            screening.started_at = datetime.now(timezone.utc)

        # ---------------------------------------------------------
        # 1. Get domain requirements
        # ---------------------------------------------------------

        domain = (
            db.query(Domain)
            .filter(Domain.id == screening.domain_id)
            .first()
        )

        if not domain:
            raise ValueError(f"Screening domain {screening.domain_id} not found.")

        domain_requirements = (
            domain.description
            if domain.description
            else domain.name
        )

        # ---------------------------------------------------------
        # 2. Get candidate processing records (PENDING or INTERRUPTED)
        # ---------------------------------------------------------

        processing_records = (
            db.query(CandidateProcessing)
            .filter(
                CandidateProcessing.screening_id == screening.id,
                CandidateProcessing.status.in_([
                    CandidateProcessingStatus.PENDING,
                    CandidateProcessingStatus.PROCESSING,
                ]),
            )
            .all()
        )

        total_in_screening = (
            db.query(CandidateProcessing)
            .filter(CandidateProcessing.screening_id == screening.id)
            .count()
        )

        screening.total_candidates = total_in_screening

        if not processing_records:
            completed_count = (
                db.query(CandidateProcessing)
                .filter(
                    CandidateProcessing.screening_id == screening.id,
                    CandidateProcessing.status == CandidateProcessingStatus.COMPLETED,
                )
                .count()
            )
            failed_count = (
                db.query(CandidateProcessing)
                .filter(
                    CandidateProcessing.screening_id == screening.id,
                    CandidateProcessing.status == CandidateProcessingStatus.FAILED,
                )
                .count()
            )

            screening.processed_candidates = completed_count
            screening.failed_candidates = failed_count
            screening.status = (
                ScreeningStatus.COMPLETED
                if (completed_count > 0 or total_in_screening == 0)
                else ScreeningStatus.FAILED
            )
            screening.completed_at = datetime.now(timezone.utc)
            db.commit()
            return

        screening.status = ScreeningStatus.IN_PROGRESS
        db.commit()

        # ---------------------------------------------------------
        # 3. Process each candidate
        # ---------------------------------------------------------

        for processing in processing_records:
            stage = ProcessingStage.EXTRACTION
            processing_id = processing.id

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

                if not resume or not resume.resume_url:
                    raise ValueError(
                        f"No valid resume URL found for candidate {candidate.id}."
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
                            "Resume download failed.",
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

                stage = ProcessingStage.EVALUATION

                ai_result = evaluate_candidate(
                    resume_text=resume_text,
                    rubric=str(RUBRIC),
                    domain_requirements=domain_requirements,
                    prompt_version="v1",
                    provider="groq",
                )

                evaluation_model = ai_result["evaluation"]
                scores = ai_result["scores"]
                metadata = ai_result.get("metadata", {})
                eval_model_name = metadata.get("model", "groq")

                # -------------------------------------------------
                # 7. Save Evaluation (SCORING stage)
                # -------------------------------------------------

                stage = ProcessingStage.SCORING

                existing_eval = (
                    db.query(Evaluation)
                    .filter(Evaluation.candidate_processing_id == processing.id)
                    .first()
                )

                if existing_eval:
                    existing_eval.model = eval_model_name
                    existing_eval.prompt_version = "v1"
                    existing_eval.rubric_version = "v1"
                    existing_eval.evaluation_data = evaluation_model.model_dump(mode="json")
                    existing_eval.technical_skills_score = scores["technical_skills"]
                    existing_eval.competitive_achievement_score = scores["competitive_achievement"]
                    existing_eval.relevant_experience_score = scores["relevant_experience"]
                    existing_eval.projects_score = scores["projects"]
                    existing_eval.demonstrated_potential_score = scores["demonstrated_potential"]
                    existing_eval.domain_relevance_score = scores["domain_relevance"]
                    existing_eval.final_score = scores["total_score"]
                    evaluation = existing_eval
                else:
                    evaluation = Evaluation(
                        candidate_processing_id=processing.id,
                        model=eval_model_name,
                        prompt_version="v1",
                        rubric_version="v1",
                        evaluation_data=evaluation_model.model_dump(mode="json"),
                        technical_skills_score=scores["technical_skills"],
                        competitive_achievement_score=scores["competitive_achievement"],
                        relevant_experience_score=scores["relevant_experience"],
                        projects_score=scores["projects"],
                        demonstrated_potential_score=scores["demonstrated_potential"],
                        domain_relevance_score=scores["domain_relevance"],
                        final_score=scores["total_score"],
                    )
                    db.add(evaluation)

                db.flush()

                # -------------------------------------------------
                # 8. Save ScreeningResult
                # -------------------------------------------------

                existing_result = (
                    db.query(ScreeningResult)
                    .filter(
                        ScreeningResult.screening_id == screening.id,
                        ScreeningResult.candidate_processing_id == processing.id,
                    )
                    .first()
                )

                if existing_result:
                    existing_result.evaluation_id = evaluation.id
                    existing_result.final_score = scores["total_score"]
                    existing_result.result_status = ScreeningResultStatus.PENDING
                else:
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

                logger.info(
                    "Candidate processed successfully: screening_id=%s candidate_id=%s score=%s",
                    screening.id,
                    candidate.id,
                    scores["total_score"],
                )

            except Exception as candidate_error:
                db.rollback()

                # Re-fetch processing record after rollback
                processing = (
                    db.query(CandidateProcessing)
                    .filter(CandidateProcessing.id == processing_id)
                    .first()
                )

                if not processing:
                    continue

                processing.status = CandidateProcessingStatus.FAILED
                processing.retry_count += 1

                err_msg = str(candidate_error)
                if len(err_msg) > 990:
                    err_msg = err_msg[:990] + "..."

                failure = ProcessingFailure(
                    candidate_processing_id=processing.id,
                    stage=stage,
                    error_code=f"{stage.value}_ERROR",
                    error_message=err_msg,
                    retry_count=processing.retry_count,
                    failed_at=datetime.now(timezone.utc),
                )

                db.add(failure)
                db.commit()

                logger.error(
                    "Candidate processing failed: screening_id=%s candidate_id=%s stage=%s error=%s",
                    screening.id,
                    processing.candidate_id,
                    stage.value,
                    err_msg,
                )

        # ---------------------------------------------------------
        # 10. Rank successfully evaluated candidates
        # ---------------------------------------------------------

        results = (
            db.query(ScreeningResult)
            .filter(ScreeningResult.screening_id == screening.id)
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
            elif rank <= (screening.selection_limit + screening.waitlist_limit):
                result.result_status = ScreeningResultStatus.WAITLISTED
            else:
                result.result_status = ScreeningResultStatus.REJECTED

        # ---------------------------------------------------------
        # 11. Update screening counters and status
        # ---------------------------------------------------------

        processed_count = (
            db.query(CandidateProcessing)
            .filter(
                CandidateProcessing.screening_id == screening.id,
                CandidateProcessing.status == CandidateProcessingStatus.COMPLETED,
            )
            .count()
        )

        failed_count = (
            db.query(CandidateProcessing)
            .filter(
                CandidateProcessing.screening_id == screening.id,
                CandidateProcessing.status == CandidateProcessingStatus.FAILED,
            )
            .count()
        )

        screening.processed_candidates = processed_count
        screening.failed_candidates = failed_count
        screening.completed_at = datetime.now(timezone.utc)

        if failed_count > 0 and processed_count == 0:
            screening.status = ScreeningStatus.FAILED
        else:
            screening.status = ScreeningStatus.COMPLETED

        db.commit()

        logger.info(
            "Screening %s completed: processed=%s failed=%s total=%s status=%s",
            screening.id,
            processed_count,
            failed_count,
            screening.total_candidates,
            screening.status.value,
        )

    except Exception as workflow_error:
        db.rollback()

        screening = (
            db.query(Screening)
            .filter(Screening.id == screening_id)
            .first()
        )

        if screening:
            screening.status = ScreeningStatus.FAILED
            screening.completed_at = datetime.now(timezone.utc)
            db.commit()

        logger.exception("Screening %s encountered fatal workflow error", screening_id)
        raise workflow_error