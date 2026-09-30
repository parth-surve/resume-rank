from ai.prompts.base import build_screening_prompt
from ai.evaluator import evaluate_candidate
from ai.schemas import CandidateEvaluation


def test_screening_prompt_contains_required_sections():
    prompt = build_screening_prompt(
        resume_text="Python developer with FastAPI experience.",
        rubric="Technical Skills /20",
        domain_requirements="Python backend development",
        version="v1",
    )

    assert "EVALUATION RUBRIC:" in prompt
    assert "DOMAIN REQUIREMENTS:" in prompt
    assert "CANDIDATE RESUME:" in prompt
    assert "OUTPUT RULES:" in prompt


def test_screening_prompt_contains_candidate_data():
    prompt = build_screening_prompt(
        resume_text="Python developer with FastAPI experience.",
        rubric="Technical Skills /20",
        domain_requirements="Python backend development",
        version="v1",
    )

    assert "Python developer with FastAPI experience." in prompt
    assert "Technical Skills /20" in prompt
    assert "Python backend development" in prompt


def test_unsupported_prompt_version_fails():
    try:
        build_screening_prompt(
            resume_text="Test resume",
            rubric="Test rubric",
            domain_requirements="Test requirements",
            version="v99",
        )
        assert False, "Expected unsupported prompt version to raise ValueError"
    except ValueError:
        assert True


def test_evaluator_returns_candidate_evaluation(monkeypatch):
    expected = CandidateEvaluation.model_validate(
        {
            "technical_skills": {
                "skill_match": {"score": 5},
                "proficiency_evidence": {"score": 4},
                "technical_depth": {"score": 1},
            },
            "competitive_achievement": {"score": 0},
            "relevant_experience": {
                "relevance_and_responsibility": {"score": 3},
                "technical_depth": {"score": 1},
                "evidence_and_impact": {"score": 1},
            },
            "projects": {
                "technical_complexity_and_depth": {"score": 3},
                "ownership_and_implementation": {"score": 4},
                "relevance_and_problem_solving": {"score": 3},
                "evidence_of_outcomes": {"score": 0},
            },
            "demonstrated_potential": {
                "learning_and_growth": {"score": 2},
                "initiative_and_ownership": {"score": 2},
                "evidence_of_trajectory": {"score": 2},
            },
            "domain_relevance": {
                "domain_alignment": {"score": 6},
            },
        }
    )


    def fake_provider(prompt, response_model):
        assert "Python developer with FastAPI experience." in prompt
        assert response_model is CandidateEvaluation
        return expected

    monkeypatch.setattr(
        "ai.evaluator.generate_with_gemini",
        fake_provider,
    )

    result = evaluate_candidate(
        resume_text="Python developer with FastAPI experience.",
        rubric="Technical Skills /20",
        domain_requirements="Python backend development",
        provider="gemini",
    )

    assert isinstance(result, dict)
    assert isinstance(result["evaluation"], CandidateEvaluation)
    assert "scores" in result
    assert "guardrails" in result