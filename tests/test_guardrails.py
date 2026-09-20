from ai.guardrails import (
    GuardrailStatus,
    check_resume_input,
    check_evaluator_output,
)


# ============================================================
# INPUT GUARDRAILS
# ============================================================

def test_clean_resume():
    result = check_resume_input(
        "Python developer with FastAPI and PostgreSQL experience."
    )

    assert result.status == GuardrailStatus.CLEAN
    assert result.flags == []


def test_empty_resume_is_blocked():
    result = check_resume_input("")

    assert result.status == GuardrailStatus.BLOCKED
    assert "EMPTY_RESUME" in result.flags


def test_whitespace_resume_is_blocked():
    result = check_resume_input("   ")

    assert result.status == GuardrailStatus.BLOCKED
    assert "EMPTY_RESUME" in result.flags


def test_non_string_input_is_blocked():
    result = check_resume_input(None)

    assert result.status == GuardrailStatus.BLOCKED
    assert "INVALID_INPUT_TYPE" in result.flags


def test_large_resume_is_blocked():
    result = check_resume_input("A" * 50_001)

    assert result.status == GuardrailStatus.BLOCKED
    assert "RESUME_TOO_LARGE" in result.flags


def test_normal_resume_whitespace_is_allowed():
    result = check_resume_input(
        "Python Developer\n\nFastAPI\tPostgreSQL\r\n"
    )

    assert result.status == GuardrailStatus.CLEAN
    assert result.flags == []


def test_unusual_control_character_is_suspicious():
    result = check_resume_input(
        "Python Developer\x00FastAPI"
    )

    assert result.status == GuardrailStatus.SUSPICIOUS
    assert "SUSPICIOUS_CONTROL_CHARACTERS" in result.flags


# ============================================================
# OUTPUT GUARDRAILS
# ============================================================

def test_clean_model_output():
    result = check_evaluator_output(
        '{"technical_skills": {"score": 10}}'
    )

    assert result.status == GuardrailStatus.CLEAN
    assert result.flags == []


def test_empty_model_output_is_blocked():
    result = check_evaluator_output("")

    assert result.status == GuardrailStatus.BLOCKED
    assert "EMPTY_MODEL_OUTPUT" in result.flags


def test_none_model_output_is_blocked():
    result = check_evaluator_output(None)

    assert result.status == GuardrailStatus.BLOCKED
    assert "EMPTY_MODEL_OUTPUT" in result.flags


def test_large_model_output_is_blocked():
    result = check_evaluator_output("A" * 20_001)

    assert result.status == GuardrailStatus.BLOCKED
    assert "MODEL_OUTPUT_TOO_LARGE" in result.flags


def test_possible_prompt_leak_is_flagged():
    result = check_evaluator_output(
        "System prompt: internal evaluator instructions"
    )

    assert result.status == GuardrailStatus.SUSPICIOUS
    assert "POSSIBLE_PROMPT_LEAK" in result.flags


def test_prompt_leak_detection_is_case_insensitive():
    result = check_evaluator_output(
        "SYSTEM INSTRUCTIONS: do something"
    )

    assert result.status == GuardrailStatus.SUSPICIOUS
    assert "POSSIBLE_PROMPT_LEAK" in result.flags