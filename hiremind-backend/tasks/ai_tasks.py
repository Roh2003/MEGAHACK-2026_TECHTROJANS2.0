import asyncio
import os
from pathlib import Path

from bson import ObjectId
from celery_app import celery_app
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import requests

from AI_Model.agent import ResumeAnalysisAgent
from AI_Model.resume_parser import ResumeParser


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env", override=False)
load_dotenv(ROOT_DIR / "services" / "application-service" / ".env", override=False)
load_dotenv(ROOT_DIR / "services" / "job-service" / ".env", override=False)


def _resolve_database_config() -> tuple[str, str]:
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "ai_recruitment")
    return mongo_uri, database_name


class RateLimitRetryableError(Exception):
    """Raised when upstream AI provider returns rate limiting and task should retry."""


def _is_rate_limit_error(exc: Exception) -> bool:
    if isinstance(exc, requests.exceptions.HTTPError):
        response = getattr(exc, "response", None)
        if response is not None and response.status_code == 429:
            return True

    text = str(exc).lower()
    return "429" in text or "too many request" in text or "rate limit" in text


async def _fetch_screening_context(application_id: str) -> dict:
    mongo_uri, database_name = _resolve_database_config()
    openrouter_api_key = (
        os.getenv("OPENROUTER_API_KEY")
        or os.getenv("openrouter_api_key")
        or os.getenv("OPENROUTER_KEY")
        or os.getenv("openrouter_key")
        or ""
    ).strip()

    if not openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY is not set")

    client = AsyncIOMotorClient(mongo_uri)
    try:
        db = client[database_name]

        application_query: dict[str, object]
        try:
            application_query = {"_id": ObjectId(application_id)}
        except Exception:
            application_query = {"_id": application_id}

        application = await db["job_applications"].find_one(application_query)
        if not application:
            raise ValueError(f"Application not found: {application_id}")

        job_id = (application.get("job_id") or "").strip()
        job = None
        if job_id:
            job = await db["job_posts"].find_one({"jobid": job_id})
            if job is None:
                try:
                    job = await db["job_posts"].find_one({"_id": ObjectId(job_id)})
                except Exception:
                    job = None

        resume_url = (application.get("resume_url") or "").strip()
        resume_text = ""
        if resume_url:
            parser = ResumeParser(base_dir=ROOT_DIR)
            resume_text = await asyncio.to_thread(parser.parse, resume_url)

        if not resume_text:
            raise ValueError(f"Could not extract resume text for application: {application_id}")

        job_description = (job.get("description") or "") if job else ""
        job_skills = (job.get("skills") or []) if job else []

        print("🤖 Calling AI model...")
        agent = ResumeAnalysisAgent(api_key=openrouter_api_key)
        try:
            result = await asyncio.to_thread(
                agent.analyze_resume_text,
                resume_text,
                job_skills,
                job_description,
            )
        except Exception as exc:
            if _is_rate_limit_error(exc):
                print(
                    f"[ai-screening] Rate limited for application={application_id}. "
                    "Task will retry automatically."
                )
                raise RateLimitRetryableError(
                    f"Rate limited while screening application {application_id}"
                ) from exc
            raise

        print("✅ AI Result:", result)

        if not isinstance(result, dict) or result.get("error"):
            raise ValueError(result.get("error", "AI screening failed"))

        overall_score = result.get("overall_score")
        strengths = result.get("strengths") or []
        weaknesses = result.get("weaknesses") or result.get("missing_skills") or []

        if isinstance(overall_score, (int, float)):
            status = "shortlisted" if overall_score >= 75 else "rejected"
        else:
            status = application.get("status") or "applied"

        await db["job_applications"].update_one(
            {"_id": application["_id"]},
            {
                "$set": {
                    "ai_score": overall_score,
                    "strengths": strengths,
                    "weaknesses": weaknesses,
                    "status": status,
                }
            },
        )

        print(f"🔥 AI Screening started for application: {application_id}")
        print("[ai-screening] application:", {
            "_id": str(application.get("_id")),
            "job_id": application.get("job_id"),
            "candidate_id": application.get("candidate_id"),
            "applicant_name": application.get("applicant_name"),
            "resume_url": resume_url,
            "status": application.get("status"),
        })
        print("[ai-screening] job:", {
            "_id": str(job.get("_id")) if job else None,
            "jobid": job.get("jobid") if job else None,
            "title": job.get("title") if job else None,
            "description": job.get("description") if job else None,
            "skills": job.get("skills") if job else None,
        })
        print("[ai-screening] resume:", {
            "source": resume_url,
            "chars": len(resume_text),
            "preview": resume_text[:500],
        })

        return {
            "status": "ai_completed",
            "application_id": application_id,
            "job_id": job_id,
            "resume_chars": len(resume_text),
            "overall_score": overall_score,
        }
    finally:
        client.close()


@celery_app.task(
    bind=True,
    name="tasks.ai_tasks.ai_screen_resume",
    autoretry_for=(RateLimitRetryableError,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=5,
)
def ai_screen_resume(self, application_id):
    print(
        f"[ai-screening] Task start application={application_id} "
        f"retry={self.request.retries}/{self.max_retries}"
    )
    return asyncio.run(_fetch_screening_context(application_id))
    