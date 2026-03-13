from __future__ import annotations

import json
import os
import re
from typing import Any, Mapping

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Gemini models (free tier compatible)
GEMINI_FLASH = "gemini-1.5-flash"
GEMINI_PRO = "gemini-1.5-pro"

MODEL_FALLBACK_ORDER = [
    GEMINI_FLASH,
    GEMINI_PRO,
    "models/gemini-flash-latest",
]

DEFAULT_MODEL = GEMINI_FLASH


class GeminiEmailAgent:
    """
    Generate personalized recruitment emails using Gemini.
    Supports selection and rejection emails.
    """

    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL):

        resolved_api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not resolved_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        self.client = genai.Client(api_key=resolved_api_key)
        self.model_name = model

    def build_prompt(
        self,
        candidate_name: str,
        job_title: str,
        status: str,
        matching_skills: list[str] | None = None,
        weaknesses: list[str] | None = None,
    ) -> str:

        matching_skills = matching_skills or []
        weaknesses = weaknesses or []

        return f"""
You are an HR assistant writing professional recruitment emails.

Candidate Name: {candidate_name}
Job Title: {job_title}
Application Status: {status}

Matching Skills:
{json.dumps(matching_skills)}

Weaknesses or Missing Skills:
{json.dumps(weaknesses)}

Instructions:

If status = accepted:
- Congratulate the candidate
- Mention their strongest matching skills
- Encourage them for next steps

If status = rejected:
- Be polite and encouraging
- Mention areas where improvement is needed
- Encourage them to apply again

Tone:
Professional, supportive, concise.

Return JSON ONLY:

{{
 "subject": "email subject",
 "body": "html formatted email body"
}}
"""

    @staticmethod
    def _clean_response_text(response_text: str) -> str:
        cleaned = response_text.strip()

        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)

        return cleaned.strip()

    def generate_email(
        self,
        candidate_name: str,
        job_title: str,
        status: str,
        matching_skills: list[str] | None = None,
        weaknesses: list[str] | None = None,
    ) -> dict[str, Any]:

        prompt = self.build_prompt(
            candidate_name,
            job_title,
            status,
            matching_skills,
            weaknesses,
        )

        models_to_try = [self.model_name] + MODEL_FALLBACK_ORDER

        response = None

        for model in models_to_try:

            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.5,
                        response_mime_type="application/json",
                    ),
                )
                break

            except Exception:
                continue

        if response is None:
            raise RuntimeError("Gemini email generation failed.")

        text = self._clean_response_text(response.text)

        return json.loads(text)
