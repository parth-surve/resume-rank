import json
import os

from dotenv import load_dotenv
from groq import Groq
from google import genai
from pydantic import BaseModel


load_dotenv()


def generate_with_groq(prompt: str, response_model: type[BaseModel]) -> BaseModel:
    """
    Send a prompt to Groq and return the response as a validated Pydantic model.
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured.")

    model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

    client = Groq(api_key=api_key)

    schema = response_model.model_json_schema()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
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
        raise ValueError("Groq returned an empty response.")

    data = json.loads(content)

    return response_model.model_validate(data)


def generate_with_gemini(prompt: str, response_model: type[BaseModel]) -> BaseModel:
    """
    Send a prompt to Gemini and return the response as a validated Pydantic model.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")

    model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

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
def generate_with_ollama(
    prompt: str,
    response_model: type[BaseModel],
) -> BaseModel:
    import requests

    model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")

    schema = response_model.model_json_schema()

    response = requests.post(
        url,
        json={
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "stream": False,
            "format": schema,
            "options": {
                "temperature": 0.1,
            },
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    content = data.get("message", {}).get("content")

    if not content:
        raise ValueError("Ollama returned an empty response.")

    return response_model.model_validate_json(content)