from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types


MODULE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = MODULE_DIR.parent

GEMINI_FLASH = "models/gemini-2.5-flash"
GEMINI_FLASH_LITE = "models/gemini-2.0-flash-lite"
GEMINI_FLASH_LATEST = "models/gemini-flash-latest"

MODEL_FALLBACK_ORDER = [
    GEMINI_FLASH,
    GEMINI_FLASH_LITE,
    GEMINI_FLASH_LATEST,
]

DEFAULT_GEMINI_MODEL = GEMINI_FLASH


load_dotenv(PROJECT_DIR / ".env", override=False)
load_dotenv(MODULE_DIR / ".env", override=False)


def _clean_json_text(response_text: str) -> str:
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def _parse_json_response(response_text: str) -> dict[str, Any]:
    cleaned = _clean_json_text(response_text)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("Gemini returned non-JSON output")
        parsed = json.loads(cleaned[start : end + 1])

    if not isinstance(parsed, dict):
        raise ValueError("Gemini JSON output must be an object")
    return parsed


def _fallback_summary(payload: dict[str, Any]) -> dict[str, Any]:
    fluency = float(payload.get("speaking_fluency", 0.0))
    confidence = float(payload.get("confidence_score", 0.0))
    correctness = float(payload.get("answer_correctness_score", 0.0))

    overall = round((0.3 * fluency) + (0.25 * confidence) + (0.45 * correctness), 2)

    return {
        "candidate_summary": (
            "Candidate showed balanced communication and technical response quality. "
            "Overall performance was evaluated from fluency, confidence, and answer correctness."
        ),
        "detailed_summary": (
            f"Fluency score={fluency}, confidence score={confidence}, correctness score={correctness}. "
            "Candidate should continue improving depth and precision for advanced questions."
        ),
        "overall_score": overall,
        "strengths": ["communication", "structured answering"],
        "improvement_areas": ["deeper technical articulation"],
    }


def generate_interview_summary(
    *,
    job_id: str,
    round_id: str,
    candidate_id: str,
    conversation: list[dict[str, Any]],
    speaking_fluency: float,
    confidence_score: float,
    answer_correctness_score: float,
    model: str = DEFAULT_GEMINI_MODEL,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Generate a detailed interview summary and overall score using Gemini."""
    resolved_api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("gemini_api_key")
    if not resolved_api_key:
        fallback = _fallback_summary(
            {
                "speaking_fluency": speaking_fluency,
                "confidence_score": confidence_score,
                "answer_correctness_score": answer_correctness_score,
            }
        )
        fallback["model"] = "fallback-no-gemini-key"
        return fallback

    client = genai.Client(api_key=resolved_api_key)

    compact_conversation = [
        {
            "speaker": str(item.get("speaker", "")).strip(),
            "message": str(item.get("message", "")).strip(),
            "timestamp": item.get("timestamp"),
        }
        for item in conversation
        if str(item.get("message", "")).strip()
    ]

    prompt_payload = {
        "job_id": job_id,
        "round_id": round_id,
        "candidate_id": candidate_id,
        "scores": {
            "speaking_fluency": speaking_fluency,
            "confidence_score": confidence_score,
            "answer_correctness_score": answer_correctness_score,
        },
        "conversation": compact_conversation,
    }

    prompt = (
        "You are an expert interview evaluator. Analyze the interview conversation and provided score metrics. "
        "Return strict JSON only with this schema: "
        "{"
        '"candidate_summary": "short paragraph", '
        '"detailed_summary": "detailed technical and communication analysis", '
        '"overall_score": number, '
        '"strengths": ["..."], '
        '"improvement_areas": ["..."]'
        "}. "
        "overall_score must be between 0 and 100 and should reflect answer correctness most strongly. "
        "Input:\n"
        + json.dumps(prompt_payload, ensure_ascii=True)
    )

    candidates: list[str] = []
    for model_name in [model, *MODEL_FALLBACK_ORDER]:
        if model_name and model_name not in candidates:
            candidates.append(model_name)

    response = None
    model_used = None
    errors: list[str] = []

    for candidate_model in candidates:
        try:
            response = client.models.generate_content(
                model=candidate_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    top_p=0.9,
                    response_mime_type="application/json",
                ),
            )
            model_used = candidate_model
            break
        except Exception as exc:
            errors.append(f"{candidate_model}: {exc}")

    if response is None or model_used is None:
        fallback = _fallback_summary(
            {
                "speaking_fluency": speaking_fluency,
                "confidence_score": confidence_score,
                "answer_correctness_score": answer_correctness_score,
            }
        )
        fallback["model"] = "fallback-gemini-error"
        fallback["errors"] = errors
        return fallback

    response_text = getattr(response, "text", "") or ""
    parsed = _parse_json_response(response_text)

    overall = parsed.get("overall_score")
    if not isinstance(overall, (int, float)):
        overall = _fallback_summary(
            {
                "speaking_fluency": speaking_fluency,
                "confidence_score": confidence_score,
                "answer_correctness_score": answer_correctness_score,
            }
        )["overall_score"]

    return {
        "model": model_used,
        "candidate_summary": str(parsed.get("candidate_summary", "")).strip(),
        "detailed_summary": str(parsed.get("detailed_summary", "")).strip(),
        "overall_score": round(max(0.0, min(100.0, float(overall))), 2),
        "strengths": parsed.get("strengths") or [],
        "improvement_areas": parsed.get("improvement_areas") or [],
    }


__all__ = ["generate_interview_summary"]