from unittest.mock import patch

import pytest

from ai.evaluator import evaluate_candidate
from ai.schemas import CandidateEvaluation


def make_mock_evaluation() -> CandidateEvaluation:
    return CandidateEvaluation.model_validate(
        {
            "technical_skills": {
                "skill_match": {
                    "score": 6,
                    "evidence": ["Python", "FastAPI"],
                    "reason": "Relevant backend skills are present.",
                },
                "proficiency_evidence": {
                    "score": 5,
                    "evidence": ["Built a FastAPI API."],
                    "reason": "Practical implementation is shown.",
                },
                "technical_depth": {
                    "score": 3,
                    "evidence": ["FastAPI project"],
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
                    "reason": "Relevant backend experience is shown.",
                },
                "technical_depth": {
                    "score": 3,
                    "evidence": ["REST APIs"],
                    "reason": "Backend implementation is demonstrated.",
                },
                "evidence_and_impact": {
                    "score": 2,
                    "evidence": ["Backend internship"],
                    "reason": "Impact is not quantified.",
                },
            },
            "projects": {
                "technical_complexity_and_depth": {
                    "score": 4,
                    "evidence": ["FastAPI resume screening API"],
                    "reason": "A technical project is demonstrated.",
                },
                "ownership_and_implementation": {
                    "score": 4,
                    "evidence": ["Built the API"],
                    "reason": "Implementation is explicitly described.",
                },
                "relevance_and_problem_solving": {
                    "score": 4,
                    "evidence": ["Resume screening API"],
                    "reason": "The project solves a relevant problem.",
                },
                "evidence_of_outcomes": {
                    "score": 1,
                    "evidence": [],
                    "reason": "No measurable outcome was provided.",
                },
            },
            "demonstrated_potential": {
                "learning_and_growth": {
                    "score": 2,
                    "evidence": ["FastAPI", "PostgreSQL"],
                    "reason": "Multiple technologies are demonstrated.",
                },
                "initiative_and_ownership": {
                    "score": 3,
                    "evidence": ["Built a resume screening API"],
                    "reason": "A concrete project demonstrates initiative.",
                },
                "evidence_of_trajectory": {
                    "score": 2,
                    "evidence": ["Backend internship"],
                    "reason": "Some progression is demonstrated.",
                },
            },
            "domain_relevance": {
                "domain_alignment": {
                    "score": 5,
                    "evidence": ["FastAPI", "Python"],
                    "reason": "Backend skills align with the requirement.",
                },
            },
        }
    )


def test_evaluate_candidate_uses_groq():
    mock_evaluation = make_mock_evaluation()

    with patch(
        "ai.evaluator.generate_with_groq",
        return_value=mock_evaluation,
    ) as mock_groq:
        result = evaluate_candidate(
            resume_text="Python developer with FastAPI experience.",
            rubric="Technical Skills /20",
            domain_requirements="Backend development",
            provider="groq",
        )

    assert result == mock_evaluation
    mock_groq.assert_called_once()

    _, kwargs = mock_groq.call_args
    assert kwargs["response_model"] is CandidateEvaluation
    assert "Python developer" in kwargs["prompt"]


def test_evaluate_candidate_uses_gemini():
    mock_evaluation = make_mock_evaluation()

    with patch(
        "ai.evaluator.generate_with_gemini",
        return_value=mock_evaluation,
    ) as mock_gemini:
        result = evaluate_candidate(
            resume_text="Python developer with FastAPI experience.",
            rubric="Technical Skills /20",
            domain_requirements="Backend development",
            provider="gemini",
        )

    assert result == mock_evaluation
    mock_gemini.assert_called_once()

    _, kwargs = mock_gemini.call_args
    assert kwargs["response_model"] is CandidateEvaluation
    assert "Python developer" in kwargs["prompt"]


def test_evaluate_candidate_rejects_unsupported_provider():
    with pytest.raises(ValueError, match="Unsupported AI provider"):
        evaluate_candidate(
            resume_text="Python developer.",
            rubric="Technical Skills /20",
            domain_requirements="Backend development",
            provider="invalid",
        )