import re
import io
import tempfile
import PyPDF2
import ast
from concurrent.futures import ThreadPoolExecutor
from typing import Iterable

from langchain_openai import ChatOpenAI


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

    def __init__(self, api_key: str, cutoff_score: int = 75):

        self.api_key = api_key
        self.cutoff_score = cutoff_score

        self.resume_text = None
        self.jd_text = None

        self.extracted_skills = []
        self.analysis_result = None

        self.resume_strengths = []
        self.resume_weaknesses = []

        self.improved_resume_path = None

        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key=self.api_key
        )

    # ---------------------------------------------------
    # TEXT EXTRACTION
    # ---------------------------------------------------

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

        with open(txt_file, "r", encoding="utf-8") as f:
            return f.read()

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

    # ---------------------------------------------------
    # SKILL ANALYSIS
    # ---------------------------------------------------

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

        response = self.llm.invoke(query).content

        match = re.search(r"\b(10|[0-9])\b", response)
        score = int(match.group(1)) if match else 0

        return {
            "skill": skill,
            "score": score,
            "reason": response
        }

    # ---------------------------------------------------
    # SEMANTIC SKILL ANALYSIS
    # ---------------------------------------------------

    def semantic_skill_analysis(self, resume_text, skills, jd_text=""):

        skill_scores = {}
        missing_skills = []
        strengths = []

        total_score = 0

        with ThreadPoolExecutor(max_workers=5) as executor:

            results = list(
                executor.map(lambda s: self.analyze_skill(resume_text, s, jd_text), skills)
            )

        for res in results:

            skill = res["skill"]
            score = res["score"]

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
            "missing_skills": missing_skills
        }

    @staticmethod
    def _extract_year_values(text: str) -> list[float]:
        if not text:
            return []

        values: list[float] = []
        normalized = text.lower()

        # Matches: 3 years, 2.5 yrs, 4+ years
        for match in re.finditer(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)", normalized):
            values.append(float(match.group(1)))

        # Matches ranges: 2-4 years (takes midpoint)
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
            # No explicit requirement in JD; assign neutral-high if candidate mentions experience.
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
            # JD does not demand certs; reward cert presence lightly.
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

        # Deduplicate while preserving order.
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

    # ---------------------------------------------------
    # SKILL EXTRACTION FROM JD
    # ---------------------------------------------------

    def extract_skills_from_jd(self, jd_text):

        prompt = f"""
Extract the main technical skills from this job description.

Return ONLY a Python list of skills.

Job description:
{jd_text}
"""

        response = self.llm.invoke(prompt)

        text = response.content.strip()

        try:
            skills = ast.literal_eval(text)

            if isinstance(skills, list):
                return skills

        except:
            pass

        return [s.strip() for s in text.split(",") if s.strip()]

    # ---------------------------------------------------
    # RESUME ANALYSIS
    # ---------------------------------------------------

    def analyze_resume(self, resume_file, role_requirements=None, custom_jd=None):

        self.resume_text = self.extract_text_from_file(resume_file)

        if not self.resume_text:
            return {"error": "Could not extract resume text."}

        if custom_jd:

            self.jd_text = self.extract_text_from_file(custom_jd)

            self.extracted_skills = self.extract_skills_from_jd(self.jd_text)

        elif role_requirements:

            self.extracted_skills = role_requirements

        else:
            self.extracted_skills = []

        self.analysis_result = self.semantic_skill_analysis(
            self.resume_text,
            self.extracted_skills,
            self.jd_text or "",
        )

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
            

        jd_skills = []
        if jd_text and jd_text.strip():
            self.jd_text = jd_text
            jd_skills = self.extract_skills_from_jd(jd_text)
        else:
            self.jd_text = ""

        self.extracted_skills = self._merge_skills(role_requirements or [], jd_skills)

        self.analysis_result = self.semantic_skill_analysis(
            self.resume_text,
            self.extracted_skills,
            self.jd_text,
        )

        self.analysis_result = self.comprehensive_analysis(
            self.resume_text,
            self.extracted_skills,
            self.jd_text,
        )

        return self.analysis_result

    # ---------------------------------------------------
    # CHAT WITH RESUME
    # ---------------------------------------------------

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

        return self.llm.invoke(prompt).content

    # ---------------------------------------------------
    # RESUME IMPROVEMENT
    # ---------------------------------------------------

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

        response = self.llm.invoke(prompt)

        improved_resume = response.content

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".txt",
            mode="w",
            encoding="utf-8"
        ) as f:

            f.write(improved_resume)

            self.improved_resume_path = f.name

        return improved_resume