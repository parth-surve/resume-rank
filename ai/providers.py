import json
import itertools
import os
import time
import logging

from dotenv import load_dotenv
from groq import Groq
from google import genai
from pydantic import BaseModel

logger = logging.getLogger(__name__)

load_dotenv()


# ============================================================
# KEY CYCLERS (Round-Robin for all providers)
# ============================================================

_groq_keys = []
_groq_key_cycle = None

def get_next_groq_key() -> str:
    global _groq_keys, _groq_key_cycle
    if not _groq_keys:
        keys_str = os.getenv("GROQ_API_KEYS", os.getenv("GROQ_API_KEY", ""))
        _groq_keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        if not _groq_keys:
            raise ValueError("No Groq API keys configured.")
        _groq_key_cycle = itertools.cycle(_groq_keys)
    return next(_groq_key_cycle)


_gemini_keys = []
_gemini_key_cycle = None

def get_next_gemini_key() -> str:
    global _gemini_keys, _gemini_key_cycle
    if not _gemini_keys:
        keys_str = os.getenv("GEMINI_API_KEYS", os.getenv("GEMINI_API_KEY", ""))
        _gemini_keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        if not _gemini_keys:
            raise ValueError("No Gemini API keys configured.")
        _gemini_key_cycle = itertools.cycle(_gemini_keys)
    return next(_gemini_key_cycle)


_cerebras_keys = []
_cerebras_key_cycle = None

def get_next_cerebras_key() -> str:
    global _cerebras_keys, _cerebras_key_cycle
    if not _cerebras_keys:
        keys_str = os.getenv("CEREBRAS_API_KEYS", os.getenv("CEREBRAS_API_KEY", ""))
        _cerebras_keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        if not _cerebras_keys:
            raise ValueError("No Cerebras API keys configured.")
        _cerebras_key_cycle = itertools.cycle(_cerebras_keys)
    return next(_cerebras_key_cycle)


# ============================================================
# CEREBRAS (Primary - fastest free inference on the planet)
# ============================================================

def generate_with_cerebras(prompt: str, response_model: type[BaseModel]) -> BaseModel:
    """
    Send a prompt to Cerebras and return the response as a validated Pydantic model.
    Cerebras uses an OpenAI-compatible REST API so we use the openai SDK.
    """
    from openai import OpenAI

    api_key = get_next_cerebras_key()
    model = os.getenv("CEREBRAS_MODEL", "llama-3.3-70b")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.cerebras.ai/v1",
    )

    schema = response_model.model_json_schema()

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": response_model.__name__,
                "strict": True,
                "schema": schema,
            },
        },
        temperature=0.1,
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("Cerebras returned an empty response.")

    return response_model.model_validate_json(content)


# ============================================================
# GROQ (Fallback #1 - round-robin keys + retry-after aware)
# ============================================================

def generate_with_groq(prompt: str, response_model: type[BaseModel]) -> BaseModel:
    """
    Send a prompt to Groq (round-robin across all GROQ_API_KEYS).
    """
    api_key = get_next_groq_key()
    model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

    client = Groq(api_key=api_key)
    schema = response_model.model_json_schema()

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": response_model.__name__,
                "strict": True,
                "schema": schema,
            },
        },
        temperature=0.1,
        max_tokens=800,
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("Groq returned an empty response.")

    return response_model.model_validate(json.loads(content))


# ============================================================
# GEMINI (Fallback #2 - round-robin keys)
# ============================================================

def generate_with_gemini(prompt: str, response_model: type[BaseModel]) -> BaseModel:
    """
    Send a prompt to Gemini (round-robin across all GEMINI_API_KEYS).
    """
    api_key = get_next_gemini_key()
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    client = genai.Client(api_key=api_key)
    schema = response_model.model_json_schema()

    # Gemini does not accept additionalProperties in response_schema.
    def clean_schema(value):
        if isinstance(value, dict):
            value.pop("additionalProperties", None)
            for nested_value in value.values():
                clean_schema(nested_value)
        elif isinstance(value, list):
            for item in value:
                clean_schema(item)

    clean_schema(schema)

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": schema,
            "temperature": 0.1,
        },
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    return response_model.model_validate_json(response.text)


# ============================================================
# OLLAMA (Local fallback - last resort)
# ============================================================

def generate_with_ollama(
    prompt: str,
    response_model: type[BaseModel],
) -> BaseModel:
    import requests
    from ai.metrics import AI_TOKENS_GENERATED, AI_TOKENS_PER_SECOND

    model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
    schema = response_model.model_json_schema()

    response = requests.post(
        url,
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "format": schema,
            "options": {"temperature": 0.1},
        },
        timeout=600,
    )

    response.raise_for_status()
    data = response.json()
    content = data.get("message", {}).get("content")

    if not content:
        raise ValueError("Ollama returned an empty response.")

    # --------------------------------------------------------
    # Surface Ollama's native token metrics into Prometheus.
    # eval_count     = output tokens generated
    # eval_duration  = nanoseconds spent generating (GPU time)
    # --------------------------------------------------------
    tokens_out = data.get("eval_count", 0)
    eval_ns = data.get("eval_duration", 0)

    if tokens_out > 0:
        AI_TOKENS_GENERATED.labels("ollama").inc(tokens_out)
        if eval_ns > 0:
            tps = tokens_out / (eval_ns / 1e9)
            AI_TOKENS_PER_SECOND.labels("ollama").observe(tps)
            logger.debug(
                "Ollama inference: tokens=%d  tok/s=%.1f", tokens_out, tps
            )

    return response_model.model_validate_json(content)