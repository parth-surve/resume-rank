import os
import re
import time
import logging
from time import perf_counter

logger = logging.getLogger(__name__)

from ai.prompts.base import build_screening_prompt
from ai.providers import (
    generate_with_cerebras,
    generate_with_groq,
    generate_with_gemini,
    generate_with_ollama,
)
from ai.schemas import CandidateEvaluation
from ai.guardrails import check_resume_input, check_evaluator_output, GuardrailStatus
from ai.validators import validate_evaluation
from ai.scoring import calculate_scores
from ai.metrics import EVALUATIONS, EVALUATION_DURATION


# ============================================================
# PROVIDER CASCADE ORDER
# Primary → Fallback #1 → Fallback #2
# ============================================================

def _get_provider_cascade(preferred: str) -> list[str]:
    """Return ordered list of providers to try, starting with preferred."""
    # Ollama is local = primary, then cloud fallbacks
    all_providers = ["ollama", "groq", "gemini"]
    # Put preferred first, then the rest in default order
    cascade = [preferred] + [p for p in all_providers if p != preferred]
    return cascade


def _parse_retry_after(error_str: str) -> float:
    """
    Parse retry-after seconds from a rate-limit error message.
    Groq and other providers often include 'try again in Xs' or
    'x-ratelimit-reset: Xs' in their error strings.
    Returns the suggested wait time, or 30.0 as default.
    """
    # Match patterns like: "try again in 45.2s", "retry after 60", "reset in 2m30s"
    patterns = [
        r"try again in (\d+\.?\d*)s",
        r"retry.{0,10}after (\d+\.?\d*)",
        r"reset.{0,10}in (\d+\.?\d*)s",
        r"(\d+\.?\d*)s before",
        r"wait (\d+\.?\d*) second",
    ]
    for pattern in patterns:
        match = re.search(pattern, error_str, re.IGNORECASE)
        if match:
            return min(float(match.group(1)) + 1.0, 120.0)  # cap at 2 min
    return 30.0  # default backoff


def _is_rate_limit_error(error_str: str) -> bool:
    return any(kw in error_str for kw in [
        "429", "Too Many Requests", "RESOURCE_EXHAUSTED",
        "rate_limit_exceeded", "tokens", "OTPM", "RPM",
    ])


def _is_server_error(error_str: str) -> bool:
    return any(kw in error_str for kw in [
        "503", "UNAVAILABLE", "overloaded", "server closed",
        "Connection", "timeout", "ServiceUnavailable",
    ])


def _should_switch_provider(error_str: str) -> bool:
    """True if the error suggests this provider is fundamentally unusable right now."""
    return any(kw in error_str for kw in [
        "decommissioned", "per day", "daily", "exceeded your",
        "billing", "quota", "PERMISSION_DENIED",
    ])


# ============================================================
# MAIN PUBLIC FUNCTION
# ============================================================

def evaluate_candidate(
    resume_text: str,
    rubric: str,
    domain_requirements: str,
    prompt_version: str = "v1",
    provider: str = "cerebras",
) -> dict:
    """
    Evaluate a candidate with automatic provider cascade.

    Tries providers in order: cerebras → groq → gemini
    Uses retry-after headers to wait only as long as needed.
    """
    started = perf_counter()
    outcome = "failure"

    cascade = _get_provider_cascade(provider)

    try:
        for current_provider in cascade:
            # No sleep for local Ollama (no rate limits!)
            # Light throttle for cloud providers to avoid rate limits
            if current_provider != "ollama":
                time.sleep(2.0)

            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    logger.info(f"Evaluating with provider={current_provider} attempt={attempt + 1}")
                    result = _evaluate_candidate(
                        resume_text, rubric, domain_requirements, prompt_version, current_provider
                    )
                    outcome = "success"
                    return result

                except Exception as e:
                    error_str = str(e)

                    # Permanently broken on this provider → try next
                    if _should_switch_provider(error_str):
                        logger.warning(f"[{current_provider}] Hard limit hit. Switching provider. Error: {error_str[:120]}")
                        break  # break inner loop → next provider in cascade

                    # Rate limit → wait smart amount then retry same provider
                    if _is_rate_limit_error(error_str):
                        wait = _parse_retry_after(error_str)
                        logger.warning(f"[{current_provider}] Rate limited. Waiting {wait:.1f}s... (attempt {attempt + 1}/{max_attempts})")
                        time.sleep(wait)
                        if attempt < max_attempts - 1:
                            continue  # retry same provider
                        else:
                            logger.warning(f"[{current_provider}] Exhausted retries on rate limit. Switching provider.")
                            break

                    # Server error → short backoff then retry
                    if _is_server_error(error_str):
                        wait = 10.0 if attempt == 0 else 30.0
                        logger.warning(f"[{current_provider}] Server error. Waiting {wait}s... (attempt {attempt + 1}/{max_attempts})")
                        time.sleep(wait)
                        if attempt < max_attempts - 1:
                            continue
                        else:
                            logger.warning(f"[{current_provider}] Server keeps failing. Switching provider.")
                            break

                    # Unknown error → don't retry, bubble up immediately
                    logger.error(f"[{current_provider}] Unrecoverable error: {error_str[:200]}")
                    raise e

        raise RuntimeError("All providers exhausted. Could not evaluate candidate.")

    finally:
        metric_provider = provider if provider in {"groq", "gemini", "ollama", "cerebras"} else "unsupported"
        EVALUATIONS.labels(metric_provider, outcome).inc()
        EVALUATION_DURATION.labels(metric_provider).observe(perf_counter() - started)


# ============================================================
# INTERNAL PIPELINE (single provider, no retry logic)
# ============================================================

def _evaluate_candidate(
    resume_text: str,
    rubric: str,
    domain_requirements: str,
    prompt_version: str = "v1",
    provider: str = "cerebras",
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

    if provider == "cerebras":
        evaluation = generate_with_cerebras(prompt=prompt, response_model=CandidateEvaluation)
    elif provider == "groq":
        evaluation = generate_with_groq(prompt=prompt, response_model=CandidateEvaluation)
    elif provider == "gemini":
        evaluation = generate_with_gemini(prompt=prompt, response_model=CandidateEvaluation)
    elif provider == "ollama":
        evaluation = generate_with_ollama(prompt=prompt, response_model=CandidateEvaluation)
    else:
        raise ValueError(f"Unsupported AI provider: {provider}")

    # --------------------------------------------------------
    # 4. OUTPUT GUARDRAILS
    # --------------------------------------------------------

    output_result = check_evaluator_output(evaluation.model_dump_json())

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

    model_defaults = {
        "cerebras": ("CEREBRAS_MODEL", "llama-3.3-70b"),
        "groq":     ("GROQ_MODEL",     "qwen/qwen3.8-27b"),
        "gemini":   ("GEMINI_MODEL",   "gemini-2.0-flash"),
        "ollama":   ("OLLAMA_MODEL",   "qwen2.5:7b"),
    }
    model_env, default_model = model_defaults.get(provider, ("", "unknown"))

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
