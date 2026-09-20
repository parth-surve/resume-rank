import pytest

from ai.schemas import CandidateEvaluation
from ai.validators import validate_evaluation


def make_valid_evaluation() -> CandidateEvaluation:
    return CandidateEvaluation.model_validate(
        {
            "technical_skills": {
                "skill_match": {
                    "score": 6,
                    "evidence": ["Python", "FastAPI"],
                    "reason": "Relevant technical skills are demonstrated.",
                },
                "proficiency_evidence": {
                    "score": 5,
                    "evidence": ["Built a FastAPI API."],
                    "reason": "Practical implementation is demonstrated.",
                },
                "technical_depth": {
                    "score": 3,
                    "evidence": ["Implemented REST APIs."],
                    "reason": "Some technical depth is demonstrated.",
                },
            },
            "competitive_achievement": {
                "score": 0,
                "evidence": [],
                "reason": "No competitive achievement was provided.",
            },
            "relevant_experience": {
                "relevance_and_responsibility": {
                    "score": 4,
                    "evidence": ["Backend internship"],
                    "reason": "Relevant backend experience is demonstrated.",
                },
                "technical_depth": {
                    "score": 3,
                    "evidence": ["REST APIs"],
                    "reason": "Technical implementation is demonstrated.",
                },
                "evidence_and_impact": {
                    "score": 2,
                    "evidence": ["Built backend APIs"],
                    "reason": "Contribution is demonstrated but impact is not quantified.",
                },
            },
            "projects": {
                "technical_complexity_and_depth": {
                    "score": 4,
                    "evidence": ["FastAPI project"],
                    "reason": "A meaningful technical project is demonstrated.",
                },
                "ownership_and_implementation": {
                    "score": 4,
                    "evidence": ["Built the API"],
                    "reason": "Implementation is explicitly described.",
                },
                "relevance_and_problem_solving": {
                    "score": 3,
                    "evidence": ["Resume screening API"],
                    "reason": "The project addresses a relevant technical problem.",
                },
                "evidence_of_outcomes": {
                    "score": 0,
                    "evidence": [],
                    "reason": "No measurable outcome was provided.",
                },
            },
            "demonstrated_potential": {
                "learning_and_growth": {
                    "score": 0,
                    "evidence": [],
                    "reason": "No explicit evidence of technical growth was provided.",
                },
                "initiative_and_ownership": {
                    "score": 3,
                    "evidence": ["Built a resume screening API"],
                    "reason": "A concrete project demonstrates initiative.",
                },
                "evidence_of_trajectory": {
                    "score": 0,
                    "evidence": [],
                    "reason": "No chronological evidence of technical progression was provided.",
                },
            },
            "domain_relevance": {
                "domain_alignment": {
                    "score": 5,
                    "evidence": ["Python", "FastAPI"],
                    "reason": "The demonstrated technical profile aligns with the domain.",
                },
            },
        }
    )


def test_valid_evaluation_has_no_errors():
    evaluation = make_valid_evaluation()

    errors = validate_evaluation(evaluation)

    assert errors == []


def test_score_above_maximum_is_rejected():
    evaluation = make_valid_evaluation()

    evaluation.technical_skills.skill_match.score = 9

    errors = validate_evaluation(evaluation)

    assert any(
        "technical_skills.skill_match.score" in error
        for error in errors
    )


def test_negative_score_is_rejected():
    evaluation = make_valid_evaluation()

    evaluation.projects.evidence_of_outcomes.score = -1

    errors = validate_evaluation(evaluation)

    assert any(
        "projects.evidence_of_outcomes.score" in error
        for error in errors
    )


def test_empty_reason_is_rejected():
    evaluation = make_valid_evaluation()

    evaluation.competitive_achievement.reason = "   "

    errors = validate_evaluation(evaluation)

    assert any(
        "competitive_achievement.reason" in error
        for error in errors
    )


def test_non_string_evidence_is_rejected():
    evaluation = make_valid_evaluation()

    evaluation.domain_relevance.domain_alignment.evidence = [123]

    errors = validate_evaluation(evaluation)

    assert any(
        "domain_relevance.domain_alignment.evidence[0]" in error
        for error in errors
    )
    