from pydantic import BaseModel, Field, ConfigDict


# ============================================================
# Per-criterion score models with correct upper bounds
# from rubric.py max_score values.
# ============================================================

class ScoreMax3(BaseModel):
    model_config = ConfigDict(extra="forbid")
    score: int = Field(ge=0, le=3, description="Score assigned to this criterion (0–3).")


class ScoreMax4(BaseModel):
    model_config = ConfigDict(extra="forbid")
    score: int = Field(ge=0, le=4, description="Score assigned to this criterion (0–4).")


class ScoreMax5(BaseModel):
    model_config = ConfigDict(extra="forbid")
    score: int = Field(ge=0, le=5, description="Score assigned to this criterion (0–5).")


class ScoreMax6(BaseModel):
    model_config = ConfigDict(extra="forbid")
    score: int = Field(ge=0, le=6, description="Score assigned to this criterion (0–6).")


class ScoreMax7(BaseModel):
    model_config = ConfigDict(extra="forbid")
    score: int = Field(ge=0, le=7, description="Score assigned to this criterion (0–7).")


class ScoreMax8(BaseModel):
    model_config = ConfigDict(extra="forbid")
    score: int = Field(ge=0, le=8, description="Score assigned to this criterion (0–8).")


class ScoreMax10(BaseModel):
    model_config = ConfigDict(extra="forbid")
    score: int = Field(ge=0, le=10, description="Score assigned to this criterion (0–10).")


class ScoreMax15(BaseModel):
    model_config = ConfigDict(extra="forbid")
    score: int = Field(ge=0, le=15, description="Score assigned to this criterion (0–15).")


# ============================================================
# Section evaluation models
# ============================================================

class TechnicalSkillsEvaluation(BaseModel):
    """
    Evaluation of the candidate's technical skills.
    skill_match:           max 8
    proficiency_evidence:  max 7
    technical_depth:       max 5
    """

    model_config = ConfigDict(extra="forbid")

    skill_match: ScoreMax8
    proficiency_evidence: ScoreMax7
    technical_depth: ScoreMax5


class RelevantExperienceEvaluation(BaseModel):
    """
    Evaluation of the candidate's relevant experience.
    relevance_and_responsibility: max 6
    technical_depth:              max 5
    evidence_and_impact:          max 4
    """

    model_config = ConfigDict(extra="forbid")

    relevance_and_responsibility: ScoreMax6
    technical_depth: ScoreMax5
    evidence_and_impact: ScoreMax4


class ProjectsEvaluation(BaseModel):
    """
    Evaluation of the candidate's projects.
    technical_complexity_and_depth: max 10
    ownership_and_implementation:   max 7
    relevance_and_problem_solving:  max 5
    evidence_of_outcomes:           max 3
    """

    model_config = ConfigDict(extra="forbid")

    technical_complexity_and_depth: ScoreMax10
    ownership_and_implementation: ScoreMax7
    relevance_and_problem_solving: ScoreMax5
    evidence_of_outcomes: ScoreMax3


class DemonstratedPotentialEvaluation(BaseModel):
    """
    Evaluation of the candidate's demonstrated potential.
    learning_and_growth:      max 5
    initiative_and_ownership: max 5
    evidence_of_trajectory:   max 5
    """

    model_config = ConfigDict(extra="forbid")

    learning_and_growth: ScoreMax5
    initiative_and_ownership: ScoreMax5
    evidence_of_trajectory: ScoreMax5


class DomainRelevanceEvaluation(BaseModel):
    """
    Evaluation of the candidate's domain relevance.
    domain_alignment: max 10
    """

    model_config = ConfigDict(extra="forbid")

    domain_alignment: ScoreMax10


class CandidateEvaluation(BaseModel):
    """
    Complete structured evaluation of a candidate.

    Score ranges per section (matching rubric.py exactly):
      technical_skills:         max 20  (8+7+5)
      competitive_achievement:  max 15
      relevant_experience:      max 15  (6+5+4)
      projects:                 max 25  (10+7+5+3)
      demonstrated_potential:   max 15  (5+5+5)
      domain_relevance:         max 10  (10)
      TOTAL:                    max 100
    """

    model_config = ConfigDict(extra="forbid")

    technical_skills: TechnicalSkillsEvaluation
    competitive_achievement: ScoreMax15
    relevant_experience: RelevantExperienceEvaluation
    projects: ProjectsEvaluation
    demonstrated_potential: DemonstratedPotentialEvaluation
    domain_relevance: DomainRelevanceEvaluation