from ai.prompts.versions import v1


def build_screening_prompt(
    resume_text: str,
    rubric: str,
    domain_requirements: str,
    version: str = "v1",
) -> str:
    """
    Build the screening prompt for a specific prompt version.
    """

    if version == "v1":
        prompt_version = v1

    else:
        raise ValueError(f"Unsupported prompt version: {version}")

    prompt = f"""
{prompt_version.SYSTEM_INSTRUCTIONS}

{prompt_version.EVALUATION_RULES}

EVALUATION RUBRIC:
{rubric}

DOMAIN REQUIREMENTS:
{domain_requirements}

CANDIDATE RESUME:
{resume_text}

{prompt_version.OUTPUT_INSTRUCTIONS}
"""

    return prompt