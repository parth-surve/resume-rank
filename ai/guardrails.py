from dataclasses import dataclass
from enum import Enum


class GuardrailStatus(str, Enum):
    CLEAN = "CLEAN"
    SUSPICIOUS = "SUSPICIOUS"
    BLOCKED = "BLOCKED"


@dataclass
class GuardrailResult:
    status: GuardrailStatus
    flags: list[str]
    reason: str | None = None


# ------------------------------------------------------------
# Resource limits
# ------------------------------------------------------------

MAX_RESUME_LENGTH = 50_000
MAX_OUTPUT_LENGTH = 20_000


# ------------------------------------------------------------
# Input guardrails
# ------------------------------------------------------------

def check_resume_input(resume_text: str) -> GuardrailResult:
    """
    Perform deterministic safety checks on raw resume text.

    This function does NOT validate candidate scores, schemas,
    rubric limits, or scoring logic. Those belong to validators/scoring.
    """

    # Type safety
    if not isinstance(resume_text, str):
        return GuardrailResult(
            status=GuardrailStatus.BLOCKED,
            flags=["INVALID_INPUT_TYPE"],
            reason="Resume input must be a string.",
        )

    # Empty input
    if not resume_text.strip():
        return GuardrailResult(
            status=GuardrailStatus.BLOCKED,
            flags=["EMPTY_RESUME"],
            reason="Resume text is empty.",
        )

    # Resource protection
    if len(resume_text) > MAX_RESUME_LENGTH:
        return GuardrailResult(
            status=GuardrailStatus.BLOCKED,
            flags=["RESUME_TOO_LARGE"],
            reason="Resume text exceeds the maximum allowed length.",
        )

    # Detect unusual control characters.
    #
    # Normal whitespace such as newline, tab and carriage return
    # is allowed because resumes naturally contain them.
    dangerous_controls = [
        char
        for char in resume_text
        if ord(char) < 32 and char not in ("\n", "\r", "\t")
    ]

    if dangerous_controls:
        return GuardrailResult(
            status=GuardrailStatus.SUSPICIOUS,
            flags=["SUSPICIOUS_CONTROL_CHARACTERS"],
            reason="Resume contains unusual control characters.",
        )

    return GuardrailResult(
        status=GuardrailStatus.CLEAN,
        flags=[],
        reason=None,
    )


# ------------------------------------------------------------
# Output guardrails
# ------------------------------------------------------------

def check_evaluator_output(output_text: str | None) -> GuardrailResult:
    """
    Perform safety checks on raw model output.

    This does NOT validate the CandidateEvaluation schema or
    rubric score limits. Those belong to validators.
    """

    # Empty output
    if output_text is None or not output_text.strip():
        return GuardrailResult(
            status=GuardrailStatus.BLOCKED,
            flags=["EMPTY_MODEL_OUTPUT"],
            reason="The evaluator returned an empty response.",
        )

    # Resource protection
    if len(output_text) > MAX_OUTPUT_LENGTH:
        return GuardrailResult(
            status=GuardrailStatus.BLOCKED,
            flags=["MODEL_OUTPUT_TOO_LARGE"],
            reason="The evaluator output exceeds the maximum allowed length.",
        )

    # We don't attempt to prove that an output contains a prompt leak
    # using a fragile list of phrases.
    #
    # Instead, obvious instruction-like output can be flagged for review.
    #
    # This is intentionally conservative and does NOT reject the
    # candidate or act as schema validation.
    suspicious_markers = (
        "system prompt:",
        "system instructions:",
        "developer message:",
        "hidden instructions:",
        "internal instructions:",
    )

    normalized_output = output_text.lower()

    if any(marker in normalized_output for marker in suspicious_markers):
        return GuardrailResult(
            status=GuardrailStatus.SUSPICIOUS,
            flags=["POSSIBLE_PROMPT_LEAK"],
            reason="Model output appears to contain evaluator instructions.",
        )

    return GuardrailResult(
        status=GuardrailStatus.CLEAN,
        flags=[],
        reason=None,
    )