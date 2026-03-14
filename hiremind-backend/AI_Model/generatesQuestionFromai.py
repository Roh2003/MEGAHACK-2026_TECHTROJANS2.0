from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Mapping

from dotenv import load_dotenv
from google import genai
from google.genai import types


MODULE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = MODULE_DIR.parent

# Supported free-tier Gemini text models exposed by the current API.
GEMINI_FLASH = "models/gemini-2.5-flash"
GEMINI_FLASH_LITE = "models/gemini-2.0-flash-lite"
GEMINI_FLASH_LATEST = "models/gemini-flash-latest"

# Only free-tier Gemini fallbacks are used here.
MODEL_FALLBACK_ORDER = [
    GEMINI_FLASH,
    GEMINI_FLASH_LITE,
    GEMINI_FLASH_LATEST,
]

DEFAULT_GEMINI_MODEL = GEMINI_FLASH


load_dotenv(PROJECT_DIR / ".env", override=False)
load_dotenv(MODULE_DIR / ".env", override=False)


class GeminiInterviewQuestionAgent:
    """Generate structured interview questions from a job description using Gemini."""

    def __init__(self, api_key: str | None = None, model: str = DEFAULT_GEMINI_MODEL) -> None:
        resolved_api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("gemini_api_key")
        if not resolved_api_key:
            raise ValueError("GEMINI_API_KEY is not set in the environment.")

        self.api_key = resolved_api_key
        self.model_name = model
        self.client = genai.Client(api_key=self.api_key)

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
                nested = GeminiInterviewQuestionAgent._normalize_job_description(value)
                if nested:
                    normalized[key] = nested
                continue

            normalized[key] = value

        if not normalized:
            raise ValueError("job_description must contain at least one non-empty field.")

        return normalized

    def build_prompt(
        self,
        job_description: Mapping[str, Any],
        questions_per_level: int = 5,
    ) -> str:
        normalized_job_description = self._normalize_job_description(job_description)
        safe_questions_per_level = max(5, questions_per_level)
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
8. Return exactly {safe_questions_per_level} questions for each level: easy, medium, and hard.
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
                raise ValueError("Gemini returned a non-JSON response.")

            parsed = json.loads(cleaned[start_index : end_index + 1])

        if not isinstance(parsed, dict):
            raise ValueError("Gemini response JSON must be an object.")

        return parsed

    def generate_questions_response(
        self,
        job_description: Mapping[str, Any],
        questions_per_level: int = 5,
    ) -> dict[str, Any]:
        prompt = self.build_prompt(job_description, questions_per_level=questions_per_level)

        candidates: list[str] = []
        for model_name in [self.model_name, *MODEL_FALLBACK_ORDER]:
            if model_name and model_name not in candidates:
                candidates.append(model_name)

        response = None
        model_used = None
        errors: list[str] = []
        for candidate_model in candidates:
            try:
                response = self.client.models.generate_content(
                    model=candidate_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                        top_p=0.9,
                        response_mime_type="application/json",
                    ),
                )
                model_used = candidate_model
                break
            except Exception as exc:
                errors.append(f"{candidate_model}: {exc}")

        if response is None or model_used is None:
            joined = " | ".join(errors)
            raise RuntimeError(
                f"Gemini request failed for all candidate models. Attempted: {', '.join(candidates)}. Details: {joined}"
            )

        response_text = getattr(response, "text", "") or ""
        if not response_text.strip():
            raise ValueError("Gemini returned an empty response.")

        return {
            "model": model_used,
            "prompt": prompt,
            "response": self._parse_response_json(response_text),
            "raw_response": self._clean_response_text(response_text),
        }


def generate_gemini_agent_response(
    job_description: Mapping[str, Any],
    questions_per_level: int = 5,
    model: str = DEFAULT_GEMINI_MODEL,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Generate interview-question data from Gemini for a job description object."""

    agent = GeminiInterviewQuestionAgent(api_key=api_key, model=model)
    safe_questions_per_level = max(5, questions_per_level)
    return agent.generate_questions_response(
        job_description=job_description,
        questions_per_level=safe_questions_per_level,
    )


__all__ = [
    "GeminiInterviewQuestionAgent",
    "generate_gemini_agent_response",
]
