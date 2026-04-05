from __future__ import annotations

import ast
import io
import json
import os
import re
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Iterable

import PyPDF2
import requests


STATIC_FREE_MODELS = [
    "meta-llama/llama-3.1-8b-instruct:free",
    "google/gemma-2-9b-it:free",
    "qwen/qwen-2.5-7b-instruct:free",
    "deepseek/deepseek-r1:free",
    "qwen/qwen3.6-plus:free",
    "liquid/lfm-2.5-1.2b-thinking:free", #10 sec
    "google/gemma-3-4b-it:free",
    "stepfun/step-3.5-flash:free",
    "minimax/minimax-m2.5:free" #26 sed
]

DEFAULT_OPENROUTER_MODEL = STATIC_FREE_MODELS[8]


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


class ResumeAnalysisAgent:
    SKILL_WEIGHT = 0.60
    EXPERIENCE_WEIGHT = 0.25
    CERTIFICATION_WEIGHT = 0.15

    CERTIFICATION_TERMS = [
        "aws",
        "azure",
        "gcp",
        "kubernetes",
        "docker",
        "terraform",
        "pmp",
        "scrum",
        "csm",
        "ccna",
        "comptia",
        "oracle",
        "salesforce",
        "itil",
    ]

    def __init__(self, api_key: str | None = None, model: str | None = None, cutoff_score: int = 75):
        self.api_key = (
            api_key
            or os.getenv("OPENROUTER_API_KEY")
            or os.getenv("openrouter_api_key")
            or os.getenv("OPENROUTER_KEY")
            or os.getenv("openrouter_key")
        )
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not set in the environment.")

        self.cutoff_score = cutoff_score
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
        self.model_name = model or os.getenv("OPENROUTER_MODEL") or DEFAULT_OPENROUTER_MODEL
        self.http_referer = os.getenv("OPENROUTER_HTTP_REFERER", "http://localhost")
        self.app_title = os.getenv("OPENROUTER_APP_TITLE", "HireMind")

        self.resume_text = None
        self.jd_text = None

        self.extracted_skills: list[str] = []
        self.analysis_result: dict[str, Any] | None = None

        self.resume_strengths: list[str] = []
        self.resume_weaknesses: list[str] = []

        self.improved_resume_path = None

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

    @staticmethod
    def _clean_response_text(response_text: str) -> str:
        cleaned = (response_text or "").strip()

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
                raise ValueError("Model returned a non-JSON response.")

            parsed = json.loads(cleaned[start_index : end_index + 1])

        if not isinstance(parsed, dict):
            raise ValueError("Model response JSON must be an object.")

        return parsed

    def extract_text_from_pdf(self, pdf_file):
        text = ""

        if hasattr(pdf_file, "getvalue"):
            pdf_bytes = io.BytesIO(pdf_file.getvalue())
            reader = PyPDF2.PdfReader(pdf_bytes)
        else:
            reader = PyPDF2.PdfReader(pdf_file)

        for page in reader.pages:
            text += page.extract_text() or ""

        return text

    def extract_text_from_txt(self, txt_file):
        if hasattr(txt_file, "getvalue"):
            return txt_file.getvalue().decode("utf-8")

        with open(txt_file, "r", encoding="utf-8") as file_handle:
            return file_handle.read()

    def extract_text_from_file(self, file):
        filename = getattr(file, "name", "") or ""
        ext = filename.split(".")[-1].lower() if "." in filename else ""

        if ext == "pdf":
            return self.extract_text_from_pdf(file)

        if ext == "txt":
            return self.extract_text_from_txt(file)

        return ""

    @staticmethod
    def _merge_skills(*skill_groups: Iterable[str]) -> list[str]:
        merged: list[str] = []
        seen: set[str] = set()
        for group in skill_groups:
            for skill in group or []:
                normalized = skill.strip()
                key = normalized.lower()
                if normalized and key not in seen:
                    seen.add(key)
                    merged.append(normalized)
        return merged

    def analyze_skill(self, resume_text, skill, jd_text=""):
        query = f"""
            Analyze the resume and rate the candidate proficiency in {skill}.

            Job description context:
            {jd_text}

            Resume text:
            {resume_text}

            Return format:
            Score: number between 0-10
            Reason: short explanation
            """

        response = self._chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Keep answers concise and clear."},
                {"role": "user", "content": query},
            ],
            prompt_label=f"skill-analysis:{skill}",
        )

        match = re.search(r"\b(10|[0-9])\b", response)
        score = int(match.group(1)) if match else 0

        return {"skill": skill, "score": score, "reason": response}

    def semantic_skill_analysis(self, resume_text, skills, jd_text=""):
        skill_scores = {}
        missing_skills = []
        strengths = []

        total_score = 0

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(lambda s: self.analyze_skill(resume_text, s, jd_text), skills))

        for result in results:
            skill = result["skill"]
            score = result["score"]

            skill_scores[skill] = score
            total_score += score

            if score <= 5:
                missing_skills.append(skill)

            if score >= 7:
                strengths.append(skill)

        overall_score = int((total_score / (10 * len(skills))) * 100) if skills else 0

        self.resume_strengths = strengths
        self.resume_weaknesses = missing_skills

        return {
            "overall_score": overall_score,
            "skill_scores": skill_scores,
            "strengths": strengths,
            "missing_skills": missing_skills,
        }

    def _build_resume_screening_prompt(self, resume_text: str, skills: list[str], jd_text: str = "") -> str:
        skills_json = json.dumps(skills or [], ensure_ascii=True, indent=2)
        jd_block = jd_text.strip() if jd_text else ""

        return f"""
Analyze this resume against these skills: {skills_json}

Job description:
{jd_block or "No job description provided."}

Resume text:
{resume_text}

Return JSON only with this structure:
{{
  "overall_score": 0,
  "skill_scores": {{
    "skill name": 0
  }},
  "strengths": ["..."],
  "weaknesses": ["..."],
  "missing_skills": ["..."],
  "summary": "short screening summary"
}}

Rules:
1. Return valid JSON only.
2. Use the provided skills and job description to judge the resume.
3. Keep scores between 0 and 100.
4. skill_scores should include the provided skills when possible.
5. If a skill is not found, assign it a low score and include it in missing_skills.
""".strip()

    def _screen_resume_once(self, resume_text: str, skills: list[str], jd_text: str = "") -> dict[str, Any]:
        prompt = self._build_resume_screening_prompt(resume_text, skills, jd_text)
        response_text = self._chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a resume screening assistant. "
                        "Always return valid JSON and do not include markdown."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            prompt_label="resume-screening",
        )

        parsed = self._parse_response_json(response_text)
        skill_scores = self._normalize_skill_scores(parsed.get("skill_scores"), skills)
        strengths = self._normalize_string_list(parsed.get("strengths"))
        weaknesses = self._normalize_string_list(parsed.get("weaknesses"))
        missing_skills = self._normalize_string_list(parsed.get("missing_skills"))

        if not missing_skills and weaknesses:
            missing_skills = list(weaknesses)
        if not weaknesses and missing_skills:
            weaknesses = list(missing_skills)

        overall_score = self._normalize_score(parsed.get("overall_score"))

        normalized = {
            "overall_score": overall_score,
            "ai_score": overall_score,
            "skill_scores": skill_scores,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "missing_skills": missing_skills,
            "summary": str(parsed.get("summary") or "").strip(),
        }

        self.resume_strengths = list(normalized["strengths"])
        self.resume_weaknesses = list(normalized["missing_skills"] or normalized["weaknesses"])
        return normalized

    @staticmethod
    def _normalize_score(value: Any) -> int:
        try:
            numeric = float(value)
        except Exception:
            numeric = 0.0
        return int(max(0, min(100, round(numeric))))

    @staticmethod
    def _normalize_string_list(value: Any) -> list[str]:
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, list):
            return []

        cleaned: list[str] = []
        seen: set[str] = set()
        for item in value:
            text = str(item or "").strip()
            key = text.lower()
            if text and key not in seen:
                seen.add(key)
                cleaned.append(text)
        return cleaned

    def _normalize_skill_scores(self, value: Any, skills: list[str]) -> dict[str, int]:
        output: dict[str, int] = {}

        if isinstance(value, dict):
            for raw_key, raw_score in value.items():
                key = str(raw_key or "").strip()
                if not key:
                    continue
                output[key] = self._normalize_score(raw_score)

        for skill in skills or []:
            key = str(skill or "").strip()
            if key and key not in output:
                output[key] = 0

        return output

    @staticmethod
    def _extract_year_values(text: str) -> list[float]:
        if not text:
            return []

        values: list[float] = []
        normalized = text.lower()

        for match in re.finditer(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)", normalized):
            values.append(float(match.group(1)))

        for match in re.finditer(
            r"(\d+(?:\.\d+)?)\s*[-to]{1,3}\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)",
            normalized,
        ):
            low = float(match.group(1))
            high = float(match.group(2))
            values.append((low + high) / 2)

        return values

    def _experience_score(self, resume_text: str, jd_text: str) -> tuple[int, dict]:
        required_values = self._extract_year_values(jd_text)
        candidate_values = self._extract_year_values(resume_text)

        required_years = max(required_values) if required_values else 0.0
        candidate_years = max(candidate_values) if candidate_values else 0.0

        if required_years <= 0:
            score = 75 if candidate_years > 0 else 55
        elif candidate_years <= 0:
            score = 20
        else:
            ratio = min(candidate_years / required_years, 1.2)
            score = int(max(0, min(100, round((ratio / 1.0) * 85))))
            if candidate_years >= required_years:
                score = max(score, 85)

        details = {
            "required_years": round(required_years, 2),
            "candidate_years": round(candidate_years, 2),
        }
        return score, details

    @classmethod
    def _find_cert_terms(cls, text: str) -> list[str]:
        if not text:
            return []

        lowered = text.lower()
        found: list[str] = []
        for term in cls.CERTIFICATION_TERMS:
            if re.search(rf"\b{re.escape(term)}\b", lowered):
                found.append(term)
        return found

    def _certification_score(self, resume_text: str, jd_text: str) -> tuple[int, dict]:
        jd_terms = self._find_cert_terms(jd_text)
        resume_terms = self._find_cert_terms(resume_text)

        jd_set = set(jd_terms)
        resume_set = set(resume_terms)
        overlap = sorted(jd_set.intersection(resume_set))

        if jd_set:
            score = int((len(overlap) / len(jd_set)) * 100)
        else:
            score = 70 if resume_set else 60

        details = {
            "jd_cert_terms": sorted(jd_set),
            "resume_cert_terms": sorted(resume_set),
            "matched_cert_terms": overlap,
        }
        return score, details

    def comprehensive_analysis(self, resume_text: str, skills: list[str], jd_text: str = "") -> dict:
        skill_analysis = self.semantic_skill_analysis(resume_text, skills, jd_text)
        skill_score = int(skill_analysis.get("overall_score", 0))

        experience_score, experience_details = self._experience_score(resume_text, jd_text)
        certification_score, certification_details = self._certification_score(resume_text, jd_text)

        weighted_score = (
            (skill_score * self.SKILL_WEIGHT)
            + (experience_score * self.EXPERIENCE_WEIGHT)
            + (certification_score * self.CERTIFICATION_WEIGHT)
        )
        overall_score = int(max(0, min(100, round(weighted_score))))

        strengths = list(skill_analysis.get("strengths", []))
        if experience_score >= 80:
            strengths.append("Relevant experience")
        if certification_score >= 80:
            strengths.append("Relevant certifications")

        missing_skills = list(skill_analysis.get("missing_skills", []))
        weaknesses = list(missing_skills)
        if experience_score < 50:
            weaknesses.append("Experience gap")
        if certification_score < 50:
            weaknesses.append("Certification gap")

        def _uniq(items: list[str]) -> list[str]:
            seen: set[str] = set()
            out: list[str] = []
            for item in items:
                key = item.lower().strip()
                if key and key not in seen:
                    seen.add(key)
                    out.append(item)
            return out

        strengths = _uniq(strengths)
        weaknesses = _uniq(weaknesses)

        return {
            "overall_score": overall_score,
            "skill_scores": skill_analysis.get("skill_scores", {}),
            "strengths": strengths,
            "missing_skills": missing_skills,
            "weaknesses": weaknesses,
            "scoring_breakdown": {
                "weights": {
                    "skills": self.SKILL_WEIGHT,
                    "experience": self.EXPERIENCE_WEIGHT,
                    "certifications": self.CERTIFICATION_WEIGHT,
                },
                "components": {
                    "skills": skill_score,
                    "experience": experience_score,
                    "certifications": certification_score,
                },
                "experience_details": experience_details,
                "certification_details": certification_details,
            },
        }

    def extract_skills_from_jd(self, jd_text):
        prompt = f"""
Extract the main technical skills from this job description.

Return ONLY a Python list of skills.

Job description:
{jd_text}
"""

        text = self._chat_completion(
            messages=[
                {"role": "system", "content": "You extract skills from job descriptions."},
                {"role": "user", "content": prompt},
            ],
            prompt_label="extract-skills-from-jd",
        ).strip()

        try:
            skills = ast.literal_eval(text)
            if isinstance(skills, list):
                return skills
        except Exception:
            pass

        return [skill.strip() for skill in text.split(",") if skill.strip()]

    def analyze_resume(self, resume_file, role_requirements=None, custom_jd=None):
        self.resume_text = self.extract_text_from_file(resume_file)

        if not self.resume_text:
            return {"error": "Could not extract resume text."}

        if custom_jd:
            self.jd_text = self.extract_text_from_file(custom_jd)
        else:
            self.jd_text = ""

        self.extracted_skills = self._merge_skills(role_requirements or [])

        try:
            self.analysis_result = self._screen_resume_once(
                self.resume_text,
                self.extracted_skills,
                self.jd_text or "",
            )
        except Exception:
            self.analysis_result = self.comprehensive_analysis(
                self.resume_text,
                self.extracted_skills,
                self.jd_text or "",
            )

        return self.analysis_result

    def analyze_resume_text(self, resume_text: str, role_requirements=None, jd_text: str | None = None):
        self.resume_text = (resume_text or "").strip()

        if not self.resume_text:
            return {"error": "Could not extract resume text."}

        self.jd_text = (jd_text or "").strip()
        self.extracted_skills = self._merge_skills(role_requirements or [])

        try:
            self.analysis_result = self._screen_resume_once(
                self.resume_text,
                self.extracted_skills,
                self.jd_text,
            )
        except Exception:
            self.analysis_result = self.comprehensive_analysis(
                self.resume_text,
                self.extracted_skills,
                self.jd_text,
            )

        return self.analysis_result

    def ask_question(self, question):
        if not self.resume_text:
            return "Please analyze a resume first."

        prompt = f"""
Answer the question based only on this resume text.

Resume text:
{self.resume_text}

Question:
{question}
"""

        return self._chat_completion(
            messages=[
                {"role": "system", "content": "Answer based only on the provided resume text."},
                {"role": "user", "content": prompt},
            ],
            prompt_label="ask-question",
        )

    def get_improved_resume(self, highlight_skills=""):
        if not self.resume_text:
            return "Analyze resume first."

        prompt = f"""
Improve the following resume.

Highlight these skills: {highlight_skills}

Resume:
{self.resume_text}

Return the improved resume text.
"""

        improved_resume = self._chat_completion(
            messages=[
                {"role": "system", "content": "Improve resumes while preserving facts from the source."},
                {"role": "user", "content": prompt},
            ],
            prompt_label="improved-resume",
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as file_handle:
            file_handle.write(improved_resume)
            self.improved_resume_path = file_handle.name

        return improved_resume