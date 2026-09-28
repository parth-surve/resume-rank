from sqlalchemy.orm import Session

from ai.evaluator import evaluate_candidate
from ai.rubric import RUBRIC
from data_pipeline.resume_downloader import download_resume_in_memory

from app.db.models import (
    CandidateMaster,
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
from app.services.screening_service import ScreeningService


def mark_candidate_failed(
    db: Session,
    processing_id: int,
    stage: ProcessingStage,
    error: Exception,
) -> None:
    processing = (
        db.query(CandidateProcessing)
        .filter(CandidateProcessing.id == processing_id)
        .first()
    )

    if not processing:
        return

    processing.status = CandidateProcessingStatus.FAILED
    processing.retry_count += 1

    failure = ProcessingFailure(
        candidate_processing_id=processing_id,
        stage=stage,
        error_code="SCREENING_PROCESSING_ERROR",
        error_message=str(error),
        retry_count=processing.retry_count,
    )

    db.add(failure)
    db.commit()


async def run_screening(
    screening_id: int,
    db: Session,
) -> None:
    screening = (
        db.query(Screening)
        .filter(Screening.id == screening_id)
        .first()
    )

    if not screening:
        return

    try:
        domain = (
            db.query(Domain)
            .filter(Domain.id == screening.domain_master_id)
            .first()
        )

        if not domain:
            raise ValueError("Screening domain not found.")

        domain_requirements = (
            domain.description
            if domain.description
            else domain.name
        )

        screening_service = ScreeningService(db)
        screening_service.prepare_candidates(screening_id)

        screening.status = ScreeningStatus.IN_PROGRESS
        db.commit()

        processing_records = (
            db.query(CandidateProcessing)
            .filter(
                CandidateProcessing.screening_id == screening_id,
                CandidateProcessing.status
                == CandidateProcessingStatus.PENDING,
            )
            .all()
        )

        for processing in processing_records:
            processing_id = processing.id
            processing.status = CandidateProcessingStatus.PROCESSING
            db.commit()

            stage = ProcessingStage.EXTRACTION

            try:
                candidate = (
                    db.query(CandidateMaster)
                    .filter(
                        CandidateMaster.id
                        == processing.candidate_master_id
                    )
                    .first()
                )

                if not candidate:
                    raise ValueError(
                        f"Candidate "
                        f"{processing.candidate_master_id} "
                        f"not found."
                    )

                resumes = (
                    db.query(Resume)
                    .filter(Resume.candidate_id == candidate.id)
                    .all()
                )

                if len(resumes) == 0:
                    raise ValueError(
                        f"No resume found for candidate "
                        f"{candidate.id}."
                    )

                if len(resumes) > 1:
                    raise ValueError(
                        f"Multiple resumes found for candidate "
                        f"{candidate.id}."
                    )

                resume = resumes[0]

                download_result = download_resume_in_memory(
                    resume.resume_url
                )

                if not download_result["success"]:
                    raise ValueError(
                        download_result.get(
                            "reason",
                            "Resume processing failed.",
                        )
                    )

                resume_text = (
                    download_result["resume_text"].strip()
                )

                if not resume_text:
                    raise ValueError(
                        "Resume text extraction returned empty text."
                    )

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

                evaluation = Evaluation(
                    candidate_processing_id=processing.id,
                    model=ai_result["metadata"]["model"],
                    prompt_version=ai_result["metadata"][
                        "prompt_version"
                    ],
                    rubric_version="v1",
                    technical_skills_score=scores[
                        "technical_skills"
                    ],
                    technical_skills_evidence=(
                        evaluation_model
                        .technical_skills
                        .skill_match
                        .evidence
                        + evaluation_model
                        .technical_skills
                        .proficiency_evidence
                        .evidence
                        + evaluation_model
                        .technical_skills
                        .technical_depth
                        .evidence
                    ),
                    technical_skills_reason="\n".join(
                        [
                            evaluation_model
                            .technical_skills
                            .skill_match
                            .reason,
                            evaluation_model
                            .technical_skills
                            .proficiency_evidence
                            .reason,
                            evaluation_model
                            .technical_skills
                            .technical_depth
                            .reason,
                        ]
                    ),
                    competitive_achievement_score=scores[
                        "competitive_achievement"
                    ],
                    competitive_achievement_evidence=(
                        evaluation_model
                        .competitive_achievement
                        .evidence
                    ),
                    competitive_achievement_reason=(
                        evaluation_model
                        .competitive_achievement
                        .reason
                    ),
                    relevant_experience_score=scores[
                        "relevant_experience"
                    ],
                    relevant_experience_evidence=(
                        evaluation_model
                        .relevant_experience
                        .relevance_and_responsibility
                        .evidence
                        + evaluation_model
                        .relevant_experience
                        .technical_depth
                        .evidence
                        + evaluation_model
                        .relevant_experience
                        .evidence_and_impact
                        .evidence
                    ),
                    relevant_experience_reason="\n".join(
                        [
                            evaluation_model
                            .relevant_experience
                            .relevance_and_responsibility
                            .reason,
                            evaluation_model
                            .relevant_experience
                            .technical_depth
                            .reason,
                            evaluation_model
                            .relevant_experience
                            .evidence_and_impact
                            .reason,
                        ]
                    ),
                    projects_score=scores["projects"],
                    projects_evidence=(
                        evaluation_model
                        .projects
                        .technical_complexity_and_depth
                        .evidence
                        + evaluation_model
                        .projects
                        .ownership_and_implementation
                        .evidence
                        + evaluation_model
                        .projects
                        .relevance_and_problem_solving
                        .evidence
                        + evaluation_model
                        .projects
                        .evidence_of_outcomes
                        .evidence
                    ),
                    projects_reason="\n".join(
                        [
                            evaluation_model
                            .projects
                            .technical_complexity_and_depth
                            .reason,
                            evaluation_model
                            .projects
                            .ownership_and_implementation
                            .reason,
                            evaluation_model
                            .projects
                            .relevance_and_problem_solving
                            .reason,
                            evaluation_model
                            .projects
                            .evidence_of_outcomes
                            .reason,
                        ]
                    ),
                    demonstrated_potential_score=scores[
                        "demonstrated_potential"
                    ],
                    demonstrated_potential_evidence=(
                        evaluation_model
                        .demonstrated_potential
                        .learning_and_growth
                        .evidence
                        + evaluation_model
                        .demonstrated_potential
                        .initiative_and_ownership
                        .evidence
                        + evaluation_model
                        .demonstrated_potential
                        .evidence_of_trajectory
                        .evidence
                    ),
                    demonstrated_potential_reason="\n".join(
                        [
                            evaluation_model
                            .demonstrated_potential
                            .learning_and_growth
                            .reason,
                            evaluation_model
                            .demonstrated_potential
                            .initiative_and_ownership
                            .reason,
                            evaluation_model
                            .demonstrated_potential
                            .evidence_of_trajectory
                            .reason,
                        ]
                    ),
                    domain_relevance_score=scores[
                        "domain_relevance"
                    ],
                    domain_relevance_evidence=(
                        evaluation_model
                        .domain_relevance
                        .domain_alignment
                        .evidence
                    ),
                    domain_relevance_reason=(
                        evaluation_model
                        .domain_relevance
                        .domain_alignment
                        .reason
                    ),
                    final_score=scores["total_score"],
                )

                db.add(evaluation)
                db.flush()

                screening_result = ScreeningResult(
                    screening_id=screening.id,
                    candidate_processing_id=processing.id,
                    evaluation_id=evaluation.id,
                    final_score=scores["total_score"],
                    result_status=ScreeningResultStatus.PENDING,
                )

                db.add(screening_result)

                processing.status = (
                    CandidateProcessingStatus.COMPLETED
                )

                db.commit()

            except Exception as candidate_error:
                db.rollback()

                mark_candidate_failed(
                    db=db,
                    processing_id=processing_id,
                    stage=stage,
                    error=candidate_error,
                )

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
                result.result_status = (
                    ScreeningResultStatus.SELECTED
                )
            elif rank <= (
                screening.selection_limit
                + screening.waitlist_limit
            ):
                result.result_status = (
                    ScreeningResultStatus.WAITLISTED
                )
            else:
                result.result_status = (
                    ScreeningResultStatus.REJECTED
                )

        db.commit()

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

        screening.processed_candidate = processed_count
        screening.failed_candidates = failed_count

        if failed_count > 0 and processed_count == 0:
            screening.status = ScreeningStatus.FAILED
        else:
            screening.status = ScreeningStatus.COMPLETED

        db.commit()

    except Exception:
        db.rollback()

        screening = (
            db.query(Screening)
            .filter(Screening.id == screening_id)
            .first()
        )

        if screening:
            screening.status = ScreeningStatus.FAILED
            db.commit()

        raise