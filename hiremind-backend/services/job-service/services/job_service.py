from datetime import datetime
import asyncio
import os
from pathlib import Path

from beanie import PydanticObjectId
from fastapi import HTTPException, status
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from AI_Model.agent import ResumeAnalysisAgent
from AI_Model.resume_parser import ResumeParser
from models.job_post import JobPost
from models.rejected_candidate_match import RejectedCandidateMatch
from schemas.job_post import JobPostCreateSchema


def _serialize_job(job: JobPost) -> dict:
    return {
        "id": str(job.id),
        "title": job.title,
        "description": job.description,
        "skills": job.skills,
        "experience": job.experience,
        "location": job.location,
        "ctc": job.ctc,
        "start_time": job.start_time.isoformat(),
        "end_time": job.end_time.isoformat(),
        "created_by": job.created_by,
        "created_at": job.created_at.isoformat(),
    }


def _serialize_rejected_candidate_match(doc: RejectedCandidateMatch) -> dict:
    return {
        "id": str(doc.id),
        "job_id": doc.job_id,
        "source_application_id": doc.source_application_id,
        "source_job_id": doc.source_job_id,
        "candidate_id": doc.candidate_id,
        "applicant_name": doc.applicant_name,
        "address": doc.address,
        "highest_qualification": doc.highest_qualification,
        "experience": doc.experience,
        "resume_url": doc.resume_url,
        "previous_ai_score": doc.previous_ai_score,
        "matched_ai_score": doc.matched_ai_score,
        "strengths": doc.strengths,
        "weaknesses": doc.weaknesses,
        "source_status": doc.source_status,
        "submit_at": doc.submit_at.isoformat() if doc.submit_at else None,
        "matched_at": doc.matched_at.isoformat(),
        "updated_at": doc.updated_at.isoformat(),
    }


ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env", override=False)
load_dotenv(ROOT_DIR / "AI_Model" / ".env", override=False)


def _build_job_matching_context(job: JobPost) -> str:
    skills = ", ".join(job.skills or [])
    return "\n".join(
        [
            f"Job Title: {job.title}",
            f"Description: {job.description}",
            f"Skills: {skills}",
            f"Experience: {job.experience}",
            f"Location: {job.location}",
            f"CTC: {job.ctc}",
        ]
    )


def _resolve_openai_api_key() -> str:
    return (
        os.getenv("OPENAI_API_KEY")
        or os.getenv("openai_api_key")
        or os.getenv("OPENAPI_API_KEY")
        or os.getenv("openapi_api_key")
        or ""
    ).strip()


async def _load_rejected_source_applications() -> list[dict]:
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "ai_recruitment")
    client = AsyncIOMotorClient(mongo_uri)
    try:
        docs = await client[database_name]["job_applications"].find(
            {
                "status": "rejected",
                "resume_url": {"$exists": True, "$nin": [None, ""]},
            }
        ).sort("submit_at", -1).to_list(length=None)
        return docs
    finally:
        client.close()


def _dedupe_rejected_applications(applications: list[dict]) -> list[dict]:
    deduped: dict[str, dict] = {}
    for application in applications:
        dedupe_key = (
            application.get("candidate_id")
            or application.get("resume_url")
            or str(application.get("_id"))
        )
        if dedupe_key not in deduped:
            deduped[dedupe_key] = application
    return list(deduped.values())


async def _rematch_rejected_candidates_for_job(job: JobPost) -> dict:
    api_key = _resolve_openai_api_key()
    if not api_key:
        return {
            "enabled": False,
            "scanned_rejected_applications": 0,
            "matched_candidates": 0,
            "top_candidate": None,
            "top_candidates": [],
        }

    applications = _dedupe_rejected_applications(await _load_rejected_source_applications())
    parser = ResumeParser(base_dir=ROOT_DIR)
    agent = ResumeAnalysisAgent(api_key=api_key)
    job_context = _build_job_matching_context(job)
    job_id = str(job.id)
    now = datetime.utcnow()

    matched_docs: list[RejectedCandidateMatch] = []
    for application in applications:
        resume_url = (application.get("resume_url") or "").strip()
        if not resume_url:
            continue

        try:
            resume_text = await asyncio.to_thread(parser.parse, resume_url)
            if not resume_text:
                continue

            result = await asyncio.to_thread(
                agent.analyze_resume_text,
                resume_text,
                job.skills,
                job_context,
            )
            if not isinstance(result, dict) or result.get("error"):
                continue

            match_doc = await RejectedCandidateMatch.find_one(
                RejectedCandidateMatch.job_id == job_id,
                RejectedCandidateMatch.source_application_id == str(application.get("_id")),
            )
            payload = {
                "job_id": job_id,
                "source_application_id": str(application.get("_id")),
                "source_job_id": str(application.get("job_id") or ""),
                "candidate_id": application.get("candidate_id"),
                "applicant_name": application.get("applicant_name") or "",
                "address": application.get("address") or "",
                "highest_qualification": application.get("highest_qualification") or "",
                "experience": application.get("experience") or "",
                "resume_url": resume_url,
                "previous_ai_score": application.get("ai_score"),
                "matched_ai_score": float(result.get("overall_score") or 0),
                "strengths": result.get("strengths") or [],
                "weaknesses": result.get("weaknesses") or result.get("missing_skills") or [],
                "source_status": application.get("status") or "rejected",
                "submit_at": application.get("submit_at"),
                "updated_at": now,
            }

            if match_doc:
                for field, value in payload.items():
                    setattr(match_doc, field, value)
                await match_doc.save()
            else:
                match_doc = RejectedCandidateMatch(
                    **payload,
                    matched_at=now,
                )
                await match_doc.insert()

            matched_docs.append(match_doc)
        except Exception:
            continue

    matched_docs.sort(key=lambda doc: doc.matched_ai_score, reverse=True)
    top_candidates = [_serialize_rejected_candidate_match(doc) for doc in matched_docs[:10]]

    return {
        "enabled": True,
        "scanned_rejected_applications": len(applications),
        "matched_candidates": len(matched_docs),
        "top_candidate": top_candidates[0] if top_candidates else None,
        "top_candidates": top_candidates,
    }


async def _get_or_404(job_id: str) -> JobPost:
    try:
        obj_id = PydanticObjectId(job_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID format",
        )
    job = await JobPost.get(obj_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    return job


async def create_job(data: JobPostCreateSchema, created_by: str) -> dict:
    job = JobPost(
        title=data.title,
        description=data.description,
        skills=data.skills,
        experience=data.experience,
        location=data.location,
        ctc=data.ctc,
        start_time=data.start_time,
        end_time=data.end_time,
        created_by=created_by,
    )
    await job.insert()
    rematch_summary = await _rematch_rejected_candidates_for_job(job)
    return {
        **_serialize_job(job),
        "rejected_candidate_rematch": rematch_summary,
    }


async def get_rejected_candidate_matches(job_id: str) -> list[dict]:
    await _get_or_404(job_id)
    docs = (
        await RejectedCandidateMatch.find(RejectedCandidateMatch.job_id == job_id)
        .sort(-RejectedCandidateMatch.matched_ai_score)
        .to_list()
    )
    return [_serialize_rejected_candidate_match(doc) for doc in docs]


async def get_all_jobs() -> list:
    jobs = await JobPost.find_all().sort(-JobPost.created_at).to_list()
    return [_serialize_job(job) for job in jobs]


async def get_job_by_id(job_id: str) -> dict:
    job = await _get_or_404(job_id)
    return _serialize_job(job)


async def delete_job(job_id: str, user_id: str) -> dict:
    job = await _get_or_404(job_id)
    if job.created_by != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this job",
        )
    await job.delete()
    return {"message": "Job deleted successfully", "job_id": job_id}
