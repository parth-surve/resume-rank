from pydantic import BaseModel, Field, ConfigDict


class CriterionEvaluation(BaseModel):
    """
    Represents the AI evaluation of one scoring criterion.
    """

    model_config = ConfigDict(extra="forbid")

    score: int = Field(
        ge=0,
        description="Score assigned to this criterion."
    )

    evidence: list[str] = Field(
        description="Evidence from the candidate information supporting the score."
    )

    reason: str = Field(
        min_length=1,
        description="Explanation for why this score was assigned."
    )


class TechnicalSkillsEvaluation(BaseModel):
    """
    Evaluation of the candidate's technical skills.
    """

    model_config = ConfigDict(extra="forbid")

    skill_match: CriterionEvaluation
    proficiency_evidence: CriterionEvaluation
    technical_depth: CriterionEvaluation


class RelevantExperienceEvaluation(BaseModel):
    """
    Evaluation of the candidate's relevant experience.
    """

    model_config = ConfigDict(extra="forbid")

    relevance_and_responsibility: CriterionEvaluation
    technical_depth: CriterionEvaluation
    evidence_and_impact: CriterionEvaluation


class ProjectsEvaluation(BaseModel):
    """
    Evaluation of the candidate's projects.
    """

    model_config = ConfigDict(extra="forbid")

    technical_complexity_and_depth: CriterionEvaluation
    ownership_and_implementation: CriterionEvaluation
    relevance_and_problem_solving: CriterionEvaluation
    evidence_of_outcomes: CriterionEvaluation


class DemonstratedPotentialEvaluation(BaseModel):
    """
    Evaluation of the candidate's demonstrated potential.
    """

    model_config = ConfigDict(extra="forbid")

    learning_and_growth: CriterionEvaluation
    initiative_and_ownership: CriterionEvaluation
    evidence_of_trajectory: CriterionEvaluation


class DomainRelevanceEvaluation(BaseModel):
    """
    Evaluation of the candidate's domain relevance.
    """

    model_config = ConfigDict(extra="forbid")

    domain_alignment: CriterionEvaluation


class CandidateEvaluation(BaseModel):
    """
    Complete structured evaluation of a candidate.
    """

    model_config = ConfigDict(extra="forbid")

    technical_skills: TechnicalSkillsEvaluation
    competitive_achievement: CriterionEvaluation
    relevant_experience: RelevantExperienceEvaluation
    projects: ProjectsEvaluation
    demonstrated_potential: DemonstratedPotentialEvaluation
    domain_relevance: DomainRelevanceEvaluation