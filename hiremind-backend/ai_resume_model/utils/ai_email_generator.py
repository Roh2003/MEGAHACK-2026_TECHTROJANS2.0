from __future__ import annotations

import json
import os
import re
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

STATIC_FREE_MODELS = [
    "meta-llama/llama-3.1-8b-instruct:free",
    "google/gemma-2-9b-it:free",
    "qwen/qwen-2.5-7b-instruct:free",
    "deepseek/deepseek-r1:free",
    "qwen/qwen3.6-plus:free",
    "liquid/lfm-2.5-1.2b-thinking:free",
    "google/gemma-3-4b-it:free",
    "stepfun/step-3.5-flash:free",
    "minimax/minimax-m2.5:free",
]

DEFAULT_OPENROUTER_MODEL = STATIC_FREE_MODELS[8]


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


class OpenRouterEmailAgent:
    """
    Generate personalized recruitment emails using OpenRouter.
    Supports selection and rejection emails.
    """

    def __init__(self, api_key: str | None = None, model: str = DEFAULT_OPENROUTER_MODEL):
        resolved_api_key = (
            api_key
            or os.getenv("OPENROUTER_API_KEY")
            or os.getenv("openrouter_api_key")
            or os.getenv("OPENROUTER_KEY")
            or os.getenv("openrouter_key")
        )

        if not resolved_api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment")

        self.api_key = resolved_api_key
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
        self.model_name = model or os.getenv("OPENROUTER_MODEL") or DEFAULT_OPENROUTER_MODEL
        self.http_referer = os.getenv("OPENROUTER_HTTP_REFERER", "http://localhost")
        self.app_title = os.getenv("OPENROUTER_APP_TITLE", "HireMind")

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

    def build_assessment_prompt(
        self,
        candidate_name: str,
        job_title: str,
        assessment_link: str,
        assessment_description: str | None = None,
    ) -> str:
        description_block = assessment_description.strip() if assessment_description else ""

        return f"""
You are an HR assistant writing a professional assessment invitation email.

Candidate Name: {candidate_name}
Job Title: {job_title}
Assessment Description: {description_block or "Assessment round"}
Assessment Link: {assessment_link}

Instructions:

Write an encouraging email telling the candidate they have moved to the next round.
Mention that this is an assessment round.
Include the assessment link clearly in the body.
Keep the tone professional, supportive, and concise.

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

    def _chat_completion(self, prompt: str, model: str) -> str:
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": self.http_referer,
                "X-Title": self.app_title,
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are an HR assistant writing professional recruitment emails. "
                            "Return valid JSON only and do not include markdown."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()

        payload = response.json()
        choice = (payload.get("choices") or [{}])[0]
        message = choice.get("message", {}) if isinstance(choice, dict) else {}
        text = _to_text(message.get("content"))

        if not text:
            raise ValueError("Empty response from OpenRouter")

        return text

    def _generate_json_email(self, prompt: str) -> dict[str, Any]:
        models_to_try = [self.model_name] + [model for model in STATIC_FREE_MODELS if model != self.model_name]

        last_error: Exception | None = None
        for model in models_to_try:
            try:
                text = self._chat_completion(prompt=prompt, model=model)
                return json.loads(self._clean_response_text(text))
            except Exception as exc:
                last_error = exc

        raise RuntimeError("OpenRouter email generation failed.") from last_error

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

        return self._generate_json_email(prompt)

    def generate_assessment_email(
        self,
        candidate_name: str,
        job_title: str,
        assessment_link: str,
        assessment_description: str | None = None,
    ) -> dict[str, Any]:
        prompt = self.build_assessment_prompt(
            candidate_name=candidate_name,
            job_title=job_title,
            assessment_link=assessment_link,
            assessment_description=assessment_description,
        )
        return self._generate_json_email(prompt)
