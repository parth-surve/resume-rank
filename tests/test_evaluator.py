"""
Evaluator tests aligned to the current implementation.

Current schema: each criterion has ONLY `score` (no evidence or reason).
Current providers: cerebras (primary), groq, gemini, ollama.
Current model defaults:
  groq   -> qwen/qwen3.8-27b
  gemini -> gemini-2.0-flash
  ollama -> qwen2.5:7b

Score breakdown for make_mock_evaluation():
  technical_skills:         6+5+3 = 14
  competitive_achievement:  0
  relevant_experience:      4+3+2 = 9
  projects:                 4+4+4+1 = 13
  demonstrated_potential:   0+3+0 = 3
  domain_relevance:         5
  total_score:              44
"""
from unittest.mock import patch

import pytest

from ai.evaluator import evaluate_candidate
from ai.schemas import CandidateEvaluation


def make_mock_evaluation() -> CandidateEvaluation:
    """
    Construct a valid CandidateEvaluation using the CURRENT schema.
    Score-only per criterion; no evidence or reason fields.

    Total: 14 + 0 + 9 + 13 + 3 + 5 = 44
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
                "relevance_and_problem_solving": {"score": 4},
                "evidence_of_outcomes": {"score": 1},
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

    assert result["evaluation"] == mock_evaluation
    assert result["scores"]["total_score"] == 44
    assert result["metadata"] == {
        "prompt_version": "v1",
        "provider": "groq",
        "model": "qwen/qwen3.8-27b",
    }
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

    assert result["evaluation"] == mock_evaluation
    assert result["scores"]["total_score"] == 44
    mock_gemini.assert_called_once()

    _, kwargs = mock_gemini.call_args

    assert kwargs["response_model"] is CandidateEvaluation
    assert "Python developer" in kwargs["prompt"]


def test_evaluate_candidate_uses_ollama():
    mock_evaluation = make_mock_evaluation()

    with patch(
        "ai.evaluator.generate_with_ollama",
        return_value=mock_evaluation,
    ) as mock_ollama:
        result = evaluate_candidate(
            resume_text="Python developer with FastAPI experience.",
            rubric="Technical Skills /20",
            domain_requirements="Backend development",
            provider="ollama",
        )

    assert result["evaluation"] == mock_evaluation
    assert result["scores"]["total_score"] == 44
    mock_ollama.assert_called_once()

    _, kwargs = mock_ollama.call_args

    assert kwargs["response_model"] is CandidateEvaluation
    assert "Python developer" in kwargs["prompt"]


def test_evaluate_candidate_rejects_unsupported_provider():
    with pytest.raises(
        ValueError,
        match="Unsupported AI provider",
    ):
        evaluate_candidate(
            resume_text="Python developer.",
            rubric="Technical Skills /20",
            domain_requirements="Backend development",
            provider="invalid",
        )


def test_evaluate_candidate_blocks_invalid_resume():
    with pytest.raises(
        ValueError,
        match="Resume text is empty",
    ):
        evaluate_candidate(
            resume_text="",
            rubric="Technical Skills /20",
            domain_requirements="Backend development",
            provider="groq",
        )
