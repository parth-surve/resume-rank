from ai.rubric import RUBRIC
from ai.schemas import CandidateEvaluation


def validate_evaluation(evaluation: CandidateEvaluation) -> list[str]:
    """
    Validate an AI-generated CandidateEvaluation.

    This validator checks:
    - required structure
    - score limits
    - evidence structure
    - non-empty reasons

    It does NOT calculate the final score.
    """

    errors: list[str] = []

    # --------------------------------------------------------
    # Helper
    # --------------------------------------------------------

    def check_criterion(
        criterion,
        rubric_section: dict,
        path: str,
    ) -> None:

        max_score = rubric_section["max_score"]

        if not isinstance(criterion.score, int):
            errors.append(f"{path}.score must be an integer.")

        elif criterion.score < 0 or criterion.score > max_score:
            errors.append(
                f"{path}.score must be between 0 and {max_score}."
            )

        if not isinstance(criterion.evidence, list):
            errors.append(f"{path}.evidence must be a list.")

        else:
            for index, evidence in enumerate(criterion.evidence):
                if not isinstance(evidence, str):
                    errors.append(
                        f"{path}.evidence[{index}] must be a string."
                    )

        if not isinstance(criterion.reason, str):
            errors.append(f"{path}.reason must be a string.")

        elif not criterion.reason.strip():
            errors.append(f"{path}.reason cannot be empty.")

    # --------------------------------------------------------
    # Technical Skills
    # --------------------------------------------------------

    technical_rubric = RUBRIC["technical_skills"]["subcriteria"]

    check_criterion(
        evaluation.technical_skills.skill_match,
        technical_rubric["skill_match"],
        "technical_skills.skill_match",
    )

    check_criterion(
        evaluation.technical_skills.proficiency_evidence,
        technical_rubric["proficiency_evidence"],
        "technical_skills.proficiency_evidence",
    )

    check_criterion(
        evaluation.technical_skills.technical_depth,
        technical_rubric["technical_depth"],
        "technical_skills.technical_depth",
    )

    # --------------------------------------------------------
    # Competitive Achievement
    # --------------------------------------------------------

    check_criterion(
        evaluation.competitive_achievement,
        RUBRIC["competitive_achievement"],
        "competitive_achievement",
    )

    # --------------------------------------------------------
    # Relevant Experience
    # --------------------------------------------------------

    experience_rubric = RUBRIC["relevant_experience"]["subcriteria"]

    check_criterion(
        evaluation.relevant_experience.relevance_and_responsibility,
        experience_rubric["relevance_and_responsibility"],
        "relevant_experience.relevance_and_responsibility",
    )

    check_criterion(
        evaluation.relevant_experience.technical_depth,
        experience_rubric["technical_depth"],
        "relevant_experience.technical_depth",
    )

    check_criterion(
        evaluation.relevant_experience.evidence_and_impact,
        experience_rubric["evidence_and_impact"],
        "relevant_experience.evidence_and_impact",
    )

    # --------------------------------------------------------
    # Projects
    # --------------------------------------------------------

    project_rubric = RUBRIC["projects"]["subcriteria"]

    check_criterion(
        evaluation.projects.technical_complexity_and_depth,
        project_rubric["technical_complexity_and_depth"],
        "projects.technical_complexity_and_depth",
    )

    check_criterion(
        evaluation.projects.ownership_and_implementation,
        project_rubric["ownership_and_implementation"],
        "projects.ownership_and_implementation",
    )

    check_criterion(
        evaluation.projects.relevance_and_problem_solving,
        project_rubric["relevance_and_problem_solving"],
        "projects.relevance_and_problem_solving",
    )

    check_criterion(
        evaluation.projects.evidence_of_outcomes,
        project_rubric["evidence_of_outcomes"],
        "projects.evidence_of_outcomes",
    )

    # --------------------------------------------------------
    # Demonstrated Potential
    # --------------------------------------------------------

    potential_rubric = RUBRIC["demonstrated_potential"]["subcriteria"]

    check_criterion(
        evaluation.demonstrated_potential.learning_and_growth,
        potential_rubric["learning_and_growth"],
        "demonstrated_potential.learning_and_growth",
    )

    check_criterion(
        evaluation.demonstrated_potential.initiative_and_ownership,
        potential_rubric["initiative_and_ownership"],
        "demonstrated_potential.initiative_and_ownership",
    )

    check_criterion(
        evaluation.demonstrated_potential.evidence_of_trajectory,
        potential_rubric["evidence_of_trajectory"],
        "demonstrated_potential.evidence_of_trajectory",
    )

    # --------------------------------------------------------
    # Domain Relevance
    # --------------------------------------------------------

    check_criterion(
        evaluation.domain_relevance.domain_alignment,
        RUBRIC["domain_relevance"]["subcriteria"]["domain_alignment"],
        "domain_relevance.domain_alignment",
    )

    return errors