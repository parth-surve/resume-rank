from pydantic import BaseModel, Field, ConfigDict


class CriterionEvaluation(BaseModel):
    """
    Represents the AI evaluation of one scoring criterion.
    """

    model_config = ConfigDict(extra="forbid")

    score: int = Field(
        ge=0, # Mininum score is called ge which is 0 an max is called le which we havne't used
        description="Score assigned to this criterion."
    )

    evidence: list[str] = Field(
        default_factory=list,
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

    skill_match: CriterionEvaluation
    proficiency_evidence: CriterionEvaluation
    technical_depth: CriterionEvaluation


class RelevantExperienceEvaluation(BaseModel):
    """
    Evaluation of the candidate's relevant experience.
    """

    relevance_and_responsibility: CriterionEvaluation
    technical_depth: CriterionEvaluation
    evidence_and_impact: CriterionEvaluation


class ProjectsEvaluation(BaseModel):
    """
    Evaluation of the candidate's projects.
    """

    technical_complexity_and_depth: CriterionEvaluation
    ownership_and_implementation: CriterionEvaluation
    relevance_and_problem_solving: CriterionEvaluation
    evidence_of_outcomes: CriterionEvaluation


class DemonstratedPotentialEvaluation(BaseModel):
    """
    Evaluation of the candidate's demonstrated potential.
    """

    learning_and_growth: CriterionEvaluation
    initiative_and_ownership: CriterionEvaluation
    evidence_of_trajectory: CriterionEvaluation


class DomainRelevanceEvaluation(BaseModel):
    """
    Evaluation of the candidate's domain relevance.
    """

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