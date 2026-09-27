import os

from ai.prompts.base import build_screening_prompt
from ai.providers import (
    generate_with_groq,
    generate_with_gemini,
    generate_with_ollama,
)
from ai.schemas import CandidateEvaluation
from ai.guardrails import check_resume_input, check_evaluator_output, GuardrailStatus
from ai.validators import validate_evaluation
from ai.scoring import calculate_scores
from ai.metrics import EVALUATIONS, EVALUATION_DURATION


def evaluate_candidate(
    resume_text: str,
    rubric: str,
    domain_requirements: str,
    prompt_version: str = "v1",
    provider: str = "groq",
) -> dict:
    """Evaluate a candidate while recording outcome and elapsed time."""
    from time import perf_counter

    started = perf_counter()
    outcome = "failure"
    try:
        result = _evaluate_candidate(
            resume_text, rubric, domain_requirements, prompt_version, provider
        )
        outcome = "success"
        return result
    finally:
        metric_provider = (
            provider if provider in {"groq", "gemini", "ollama"} else "unsupported"
        )
        EVALUATIONS.labels(metric_provider, outcome).inc()
        EVALUATION_DURATION.labels(metric_provider).observe(
            perf_counter() - started
        )


def _evaluate_candidate(
    resume_text: str,
    rubric: str,
    domain_requirements: str,
    prompt_version: str = "v1",
    provider: str = "groq",
) -> dict:
    """
    Evaluate a candidate resume through the complete AI pipeline.

    Pipeline:
        Input Guardrails
        -> Prompt
        -> AI Provider
        -> Output Guardrails
        -> Validators
        -> Deterministic Scoring
    """

    # --------------------------------------------------------
    # 1. INPUT GUARDRAILS
    # --------------------------------------------------------

    guardrail_result = check_resume_input(resume_text)

    if guardrail_result.status == GuardrailStatus.BLOCKED:
        raise ValueError(
            guardrail_result.reason
            or "Resume input blocked by guardrails."
        )

    # --------------------------------------------------------
    # 2. BUILD PROMPT
    # --------------------------------------------------------

    prompt = build_screening_prompt(
        resume_text=resume_text,
        rubric=rubric,
        domain_requirements=domain_requirements,
        version=prompt_version,
    )

    # --------------------------------------------------------
    # 3. AI PROVIDER
    # --------------------------------------------------------

    if provider == "groq":
        evaluation = generate_with_groq(
        prompt=prompt,
        response_model=CandidateEvaluation,
    )
    elif provider == "gemini":
        evaluation = generate_with_gemini(
        prompt=prompt,
        response_model=CandidateEvaluation,
    )
    elif provider == "ollama":
        evaluation = generate_with_ollama(
        prompt=prompt,
        response_model=CandidateEvaluation,
    )
    else:
        raise ValueError(f"Unsupported AI provider: {provider}")

    # --------------------------------------------------------
    # 4. OUTPUT GUARDRAILS
    # --------------------------------------------------------
    #
    # Providers currently return a validated Pydantic model,
    # so we convert it to JSON only for the output safety check.

    output_result = check_evaluator_output(
        evaluation.model_dump_json()
    )

    if output_result.status == GuardrailStatus.BLOCKED:
        raise ValueError(
            output_result.reason
            or "Model output blocked by guardrails."
        )

    # --------------------------------------------------------
    # 5. VALIDATION
    # --------------------------------------------------------

    validation_errors = validate_evaluation(evaluation)

    if validation_errors:
        raise ValueError(
            "Invalid evaluation: "
            + "; ".join(validation_errors)
        )

    # --------------------------------------------------------
    # 6. DETERMINISTIC SCORING
    # --------------------------------------------------------

    scores = calculate_scores(evaluation)

    # --------------------------------------------------------
    # 7. FINAL RESULT
    # --------------------------------------------------------

    model_env, default_model = {
        "groq": ("GROQ_MODEL", "qwen/qwen3.8-27b"),
        "gemini": ("GEMINI_MODEL", "gemini-3.6-flash"),
        "ollama": ("OLLAMA_MODEL", "qwen2.5:7b"),
    }[provider]

    return {
        "evaluation": evaluation,
        "scores": scores,
        "metadata": {
            "prompt_version": prompt_version,
            "provider": provider,
            "model": os.getenv(model_env, default_model),
        },
        "guardrails": {
            "input": {
                "status": guardrail_result.status.value,
                "flags": guardrail_result.flags,
            },
            "output": {
                "status": output_result.status.value,
                "flags": output_result.flags,
            },
        },
    }
