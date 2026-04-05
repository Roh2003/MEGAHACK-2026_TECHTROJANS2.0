from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Mapping

import requests
from dotenv import load_dotenv


MODULE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = MODULE_DIR.parent

STATIC_FREE_MODELS = [
    "meta-llama/llama-3.1-8b-instruct:free",
    "google/gemma-2-9b-it:free",
    "qwen/qwen-2.5-7b-instruct:free",
    "deepseek/deepseek-r1:free",
    "qwen/qwen3.6-plus:free",
    "liquid/lfm-2.5-1.2b-thinking:free", #10 sec
    "google/gemma-3-4b-it:free",
    "stepfun/step-3.5-flash:free",
    "minimax/minimax-m2.5:free" #sed
]

DEFAULT_OPENROUTER_MODEL = STATIC_FREE_MODELS[5]


load_dotenv(PROJECT_DIR / ".env", override=False)
load_dotenv(MODULE_DIR / ".env", override=False)


def _unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(item for item in items if item))


def _to_text(content: Any) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item.get("text") or ""))
        return "".join(parts).strip()

    return ""


class OpenRouterInterviewQuestionAgent:
    """Generate structured interview questions from a job description using OpenRouter."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        resolved_api_key = (
            api_key
            or os.getenv("OPENROUTER_API_KEY")
            or os.getenv("openrouter_api_key")
            or os.getenv("OPENROUTER_KEY")
            or os.getenv("openrouter_key")
        )
        if not resolved_api_key:
            raise ValueError("OPENROUTER_API_KEY is not set in the environment.")

        self.api_key = resolved_api_key
        self.model_name = model or DEFAULT_OPENROUTER_MODEL
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
        self.http_referer = os.getenv("OPENROUTER_HTTP_REFERER", "http://localhost")
        self.app_title = os.getenv("OPENROUTER_APP_TITLE", "HireMind")

    @staticmethod
    def _normalize_job_description(job_description: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(job_description, Mapping):
            raise TypeError("job_description must be a mapping-like object.")

        normalized: dict[str, Any] = {}
        for key, value in job_description.items():
            if value is None:
                continue

            if isinstance(value, str):
                cleaned = value.strip()
                if cleaned:
                    normalized[key] = cleaned
                continue

            if isinstance(value, (list, tuple, set)):
                cleaned_items = []
                for item in value:
                    if item is None:
                        continue
                    if isinstance(item, str):
                        stripped = item.strip()
                        if stripped:
                            cleaned_items.append(stripped)
                    else:
                        cleaned_items.append(item)

                if cleaned_items:
                    normalized[key] = cleaned_items
                continue

            if isinstance(value, Mapping):
                nested = OpenRouterInterviewQuestionAgent._normalize_job_description(value)
                if nested:
                    normalized[key] = nested
                continue

            normalized[key] = value

        if not normalized:
            raise ValueError("job_description must contain at least one non-empty field.")

        return normalized

    def build_prompt(self, job_description: Mapping[str, Any], questions_per_level: int = 10) -> str:
        normalized_job_description = self._normalize_job_description(job_description)
        safe_questions_per_level = max(10, questions_per_level)
        job_payload = json.dumps(normalized_job_description, indent=2, ensure_ascii=True)

        return f"""
You are a senior hiring-panel designer and structured interview architect.

Your task is to create accurate, role-specific interview questions using only the provided job description data.
Use the role name, required skills, experience level, location, responsibilities, tools, domain context, and any other provided hiring details.

Job description object:
{job_payload}

Instructions:
1. Generate interview questions in progressive difficulty order: easy, medium, then hard.
2. Tailor every question to the exact role and skills in the job description.
3. Cover technical depth, practical execution, scenario-based thinking, and communication where relevant.
4. Avoid generic filler questions unless the job description itself is generic.
5. Do not invent company-specific facts, certifications, technologies, or domain constraints that are not supported by the job description.
6. If information is missing, stay conservative and rely only on the provided fields.
7. Make the questions useful for a real interviewer and suitable for evaluating the candidate from screening round to deep technical round.
8. Return exactly {safe_questions_per_level} questions total, mixed across easy, medium, and hard levels.
9. Order the questions from easiest to hardest.

Return valid JSON only. Do not wrap the JSON in markdown.

Required JSON schema:
{{
  "job_summary": "short summary of the role based on the provided job description",
  "interview_strategy": "brief explanation of how the questions align with the role",
    "questions": [
    {{
      "level": "easy | medium | hard",
      "category": "technical | behavioral | scenario | problem-solving | leadership | communication",
      "question": "interview question text",
      "purpose": "what this question measures",
      "expected_topics": ["topic 1", "topic 2"],
      "difficulty_reason": "why this question belongs to this difficulty level"
    }}
  ]
}}
""".strip()

    @staticmethod
    def _clean_response_text(response_text: str) -> str:
        cleaned = response_text.strip()

        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)

        return cleaned.strip()

    @classmethod
    def _parse_response_json(cls, response_text: str) -> dict[str, Any]:
        cleaned = cls._clean_response_text(response_text)

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            start_index = cleaned.find("{")
            end_index = cleaned.rfind("}")
            if start_index == -1 or end_index == -1 or end_index <= start_index:
                raise ValueError("OpenRouter returned a non-JSON response.")

            parsed = json.loads(cleaned[start_index : end_index + 1])

        if not isinstance(parsed, dict):
            raise ValueError("OpenRouter response JSON must be an object.")

        return parsed

    def _chat_completion(self, messages: list[dict[str, Any]], prompt_label: str = "") -> str:
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": self.http_referer,
                "X-Title": self.app_title,
            },
            json={
                "model": self.model_name,
                "messages": messages,
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        choice = (payload.get("choices") or [{}])[0]
        text = _to_text(choice.get("message", {}).get("content"))
        if not text:
            raise ValueError("Empty response from model")
        return text

    def generate_questions_response(self, job_description: Mapping[str, Any], questions_per_level: int = 10) -> dict[str, Any]:
        prompt = self.build_prompt(job_description, questions_per_level=questions_per_level)

        response_text = self._chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "You generate structured interview questions and always return valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            prompt_label="generate-interview-questions",
        )

        return self._parse_response_json(response_text)


def generate_gemini_agent_response(
    job_description: Mapping[str, Any],
    questions_per_level: int = 10,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Generate interview-question data from OpenRouter for a job description object."""

    agent = OpenRouterInterviewQuestionAgent(api_key=api_key, model=DEFAULT_OPENROUTER_MODEL)
    safe_questions_per_level = max(10, questions_per_level)
    return agent.generate_questions_response(job_description=job_description, questions_per_level=safe_questions_per_level)


__all__ = [
    "OpenRouterInterviewQuestionAgent",
    "generate_gemini_agent_response",
]