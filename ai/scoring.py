from ai.rubric import RUBRIC
from ai.schemas import CandidateEvaluation


def calculate_scores(evaluation: CandidateEvaluation) -> dict:
    """
    Calculate section totals and final score from a validated evaluation.

    The AI provides criterion-level scores.
    This function deterministically calculates the totals.

    Returns:
        {
            "technical_skills": int,
            "competitive_achievement": int,
            "relevant_experience": int,
            "projects": int,
            "demonstrated_potential": int,
            "domain_relevance": int,
            "total_score": int,
        }
    """

    technical_skills = (
        evaluation.technical_skills.skill_match.score
        + evaluation.technical_skills.proficiency_evidence.score
        + evaluation.technical_skills.technical_depth.score
    )

    competitive_achievement = (
        evaluation.competitive_achievement.score
    )

    relevant_experience = (
        evaluation.relevant_experience.relevance_and_responsibility.score
        + evaluation.relevant_experience.technical_depth.score
        + evaluation.relevant_experience.evidence_and_impact.score
    )

    projects = (
        evaluation.projects.technical_complexity_and_depth.score
        + evaluation.projects.ownership_and_implementation.score
        + evaluation.projects.relevance_and_problem_solving.score
        + evaluation.projects.evidence_of_outcomes.score
    )

    demonstrated_potential = (
        evaluation.demonstrated_potential.learning_and_growth.score
        + evaluation.demonstrated_potential.initiative_and_ownership.score
        + evaluation.demonstrated_potential.evidence_of_trajectory.score
    )

    domain_relevance = (
        evaluation.domain_relevance.domain_alignment.score
    )

    total_score = (
        technical_skills
        + competitive_achievement
        + relevant_experience
        + projects
        + demonstrated_potential
        + domain_relevance
    )

    return {
        "technical_skills": technical_skills,
        "competitive_achievement": competitive_achievement,
        "relevant_experience": relevant_experience,
        "projects": projects,
        "demonstrated_potential": demonstrated_potential,
        "domain_relevance": domain_relevance,
        "total_score": total_score,
    }