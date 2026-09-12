from ai.prompts.base import build_screening_prompt


def evaluate_candidate(
    resume_text: str,
    rubric: str,
    domain_requirements: str,
    prompt_version: str = "v1",
) -> str:
    """
    Build the screening prompt for a candidate.

    The LLM call will be added later.
    """

    prompt = build_screening_prompt(
        resume_text=resume_text,
        rubric=rubric,
        domain_requirements=domain_requirements,
        version=prompt_version,
    )

    return prompt