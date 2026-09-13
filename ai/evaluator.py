from ai.prompts.base import build_screening_prompt
from ai.providers import generate_with_groq, generate_with_gemini
from ai.schemas import CandidateEvaluation


def evaluate_candidate(
    resume_text: str,
    rubric: str,
    domain_requirements: str,
    prompt_version: str = "v1",
    provider: str = "groq",
) -> CandidateEvaluation:
    """
    Evaluate a candidate resume using the selected AI provider.
    """

    # Build the screening prompt
    prompt = build_screening_prompt(
        resume_text=resume_text,
        rubric=rubric,
        domain_requirements=domain_requirements,
        version=prompt_version,
    )

    # Send the prompt to the selected provider
    if provider == "groq":
        return generate_with_groq(
            prompt=prompt,
            response_model=CandidateEvaluation,
        )

    if provider == "gemini":
        return generate_with_gemini(
            prompt=prompt,
            response_model=CandidateEvaluation,
        )

    raise ValueError(f"Unsupported AI provider: {provider}")