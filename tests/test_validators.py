"""
Validator tests aligned to the current CandidateEvaluation schema.

Current schema (ai/schemas.py):
- Each criterion is a ScoreMaxN model with only `score: int` and extra="forbid".
- There is NO evidence or reason field in any criterion.

Tests preserve their original intent:
- valid evaluation has no errors
- score above maximum is rejected
- negative score is rejected

Two tests (test_empty_reason_is_rejected, test_non_string_evidence_is_rejected)
existed to guard fields that no longer exist in the schema (reason, evidence).
The equivalent invariant in the current schema is that NO extra fields are
allowed at all (extra="forbid"). These tests are replaced with a test that
verifies the schema rejects extra/forbidden fields.
"""
import pytest
from pydantic import ValidationError

from ai.schemas import CandidateEvaluation
from ai.validators import validate_evaluation


def make_valid_evaluation() -> CandidateEvaluation:
    """
    Construct a valid CandidateEvaluation using the CURRENT schema.

    Current schema: each criterion has ONLY `score`. No evidence or reason.
    Scores chosen to match the original test's arithmetic so test_scoring.py
    expectations remain unchanged:
      technical_skills:         6+5+3 = 14
      competitive_achievement:  0
      relevant_experience:      4+3+2 = 9
      projects:                 4+4+3+0 = 11
      demonstrated_potential:   0+3+0 = 3
      domain_relevance:         5
      total_score:              42
    """
    return CandidateEvaluation.model_validate(
        {
            "technical_skills": {
                "skill_match": {"score": 6},
                "proficiency_evidence": {"score": 5},
                "technical_depth": {"score": 3},
            },
            "competitive_achievement": {"score": 0},
            "relevant_experience": {
                "relevance_and_responsibility": {"score": 4},
                "technical_depth": {"score": 3},
                "evidence_and_impact": {"score": 2},
            },
            "projects": {
                "technical_complexity_and_depth": {"score": 4},
                "ownership_and_implementation": {"score": 4},
                "relevance_and_problem_solving": {"score": 3},
                "evidence_of_outcomes": {"score": 0},
            },
            "demonstrated_potential": {
                "learning_and_growth": {"score": 0},
                "initiative_and_ownership": {"score": 3},
                "evidence_of_trajectory": {"score": 0},
            },
            "domain_relevance": {
                "domain_alignment": {"score": 5},
            },
        }
    )


def test_valid_evaluation_has_no_errors():
    evaluation = make_valid_evaluation()

    errors = validate_evaluation(evaluation)

    assert errors == []


def test_score_above_maximum_is_rejected():
    """skill_match has max 8 — setting 9 must be flagged."""
    evaluation = make_valid_evaluation()

    # Directly mutate the score beyond its Pydantic-validated max
    evaluation.technical_skills.skill_match.score = 9

    errors = validate_evaluation(evaluation)

    assert any(
        "technical_skills.skill_match.score" in error
        for error in errors
    )


def test_negative_score_is_rejected():
    """evidence_of_outcomes has min 0 — setting -1 must be flagged."""
    evaluation = make_valid_evaluation()

    evaluation.projects.evidence_of_outcomes.score = -1

    errors = validate_evaluation(evaluation)

    assert any(
        "projects.evidence_of_outcomes.score" in error
        for error in errors
    )


def test_schema_rejects_extra_fields():
    """
    The current schema uses extra='forbid' on every model.

    Passing old-style fields (evidence, reason) must raise a ValidationError.
    This replaces the old test_empty_reason_is_rejected and
    test_non_string_evidence_is_rejected tests whose fields no longer exist.
    """
    with pytest.raises(ValidationError):
        CandidateEvaluation.model_validate(
            {
                "technical_skills": {
                    # 'evidence' and 'reason' are NOT part of the current schema
                    "skill_match": {
                        "score": 5,
                        "evidence": ["Python"],
                        "reason": "Some reason",
                    },
                    "proficiency_evidence": {"score": 4},
                    "technical_depth": {"score": 2},
                },
                "competitive_achievement": {"score": 0},
                "relevant_experience": {
                    "relevance_and_responsibility": {"score": 3},
                    "technical_depth": {"score": 2},
                    "evidence_and_impact": {"score": 1},
                },
                "projects": {
                    "technical_complexity_and_depth": {"score": 3},
                    "ownership_and_implementation": {"score": 3},
                    "relevance_and_problem_solving": {"score": 2},
                    "evidence_of_outcomes": {"score": 0},
                },
                "demonstrated_potential": {
                    "learning_and_growth": {"score": 1},
                    "initiative_and_ownership": {"score": 2},
                    "evidence_of_trajectory": {"score": 1},
                },
                "domain_relevance": {
                    "domain_alignment": {"score": 5},
                },
            }
        )


def test_all_criteria_at_zero_are_valid():
    """A zero score across all criteria is a valid (though poor) evaluation."""
    evaluation = CandidateEvaluation.model_validate(
        {
            "technical_skills": {
                "skill_match": {"score": 0},
                "proficiency_evidence": {"score": 0},
                "technical_depth": {"score": 0},
            },
            "competitive_achievement": {"score": 0},
            "relevant_experience": {
                "relevance_and_responsibility": {"score": 0},
                "technical_depth": {"score": 0},
                "evidence_and_impact": {"score": 0},
            },
            "projects": {
                "technical_complexity_and_depth": {"score": 0},
                "ownership_and_implementation": {"score": 0},
                "relevance_and_problem_solving": {"score": 0},
                "evidence_of_outcomes": {"score": 0},
            },
            "demonstrated_potential": {
                "learning_and_growth": {"score": 0},
                "initiative_and_ownership": {"score": 0},
                "evidence_of_trajectory": {"score": 0},
            },
            "domain_relevance": {
                "domain_alignment": {"score": 0},
            },
        }
    )

    errors = validate_evaluation(evaluation)
    assert errors == []


def test_all_criteria_at_maximum_are_valid():
    """Maximum scores across all criteria must be accepted."""
    evaluation = CandidateEvaluation.model_validate(
        {
            "technical_skills": {
                "skill_match": {"score": 8},
                "proficiency_evidence": {"score": 7},
                "technical_depth": {"score": 5},
            },
            "competitive_achievement": {"score": 15},
            "relevant_experience": {
                "relevance_and_responsibility": {"score": 6},
                "technical_depth": {"score": 5},
                "evidence_and_impact": {"score": 4},
            },
            "projects": {
                "technical_complexity_and_depth": {"score": 10},
                "ownership_and_implementation": {"score": 7},
                "relevance_and_problem_solving": {"score": 5},
                "evidence_of_outcomes": {"score": 3},
            },
            "demonstrated_potential": {
                "learning_and_growth": {"score": 5},
                "initiative_and_ownership": {"score": 5},
                "evidence_of_trajectory": {"score": 5},
            },
            "domain_relevance": {
                "domain_alignment": {"score": 10},
            },
        }
    )

    errors = validate_evaluation(evaluation)
    assert errors == []