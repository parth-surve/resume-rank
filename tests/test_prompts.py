from ai.prompts.base import build_screening_prompt
from ai.evaluator import evaluate_candidate

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

def test_evaluator_builds_screening_prompt():
    prompt = evaluate_candidate(
        resume_text="Python developer with FastAPI experience.",
        rubric="Technical Skills /20",
        domain_requirements="Python backend development",
    )

    assert "Python developer with FastAPI experience." in prompt
    assert "Technical Skills /20" in prompt
    assert "Python backend development" in prompt
    assert "OUTPUT RULES:" in prompt