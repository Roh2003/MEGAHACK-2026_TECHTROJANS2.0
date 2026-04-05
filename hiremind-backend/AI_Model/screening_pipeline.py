from __future__ import annotations

import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from AI_Model.agent import ResumeAnalysisAgent
from AI_Model.resume_parser import ResumeParser


class ScreeningPipeline:
    """Runs AI resume screening for applications of expired job posts."""

    @staticmethod
    def _log(message: str) -> None:
        print(f"[ai-screening] {message}", flush=True)

    def __init__(
        self,
        mongo_uri: str,
        database_name: str,
        openrouter_api_key: str,
        base_dir: str | Path,
        cutoff_score: int = 75,
    ) -> None:
        self._log("Step 0: Initializing screening pipeline")
        self.mongo_uri = mongo_uri
        self.database_name = database_name
        self.cutoff_score = cutoff_score

        self.client = AsyncIOMotorClient(self.mongo_uri)
        self.db = self.client[self.database_name]

        self.job_posts = self.db["job_posts"]
        self.job_applications = self.db["job_applications"]

        self.parser = ResumeParser(base_dir=base_dir)
        self.agent = ResumeAnalysisAgent(api_key=openrouter_api_key, cutoff_score=cutoff_score)
        self._log(
            f"Step 0: Pipeline initialized (db={self.database_name}, cutoff={self.cutoff_score})"
        )

    async def close(self) -> None:
        self.client.close()

    async def run_once(self) -> dict[str, Any]:
        now = datetime.utcnow()
        self._log(f"Step 1: Starting AI screening run at {now.isoformat()}")

        expired_jobs = await self.job_posts.find(
            {"end_time": {"$lte": now}}
        ).to_list(length=None)
        self._log(f"Step 2: Found expired jobs={len(expired_jobs)}")

        summary: dict[str, Any] = {
            "checked_at": now.isoformat(),
            "expired_jobs": len(expired_jobs),
            "processed_jobs": 0,
            "processed_applications": 0,
            "updated_applications": 0,
            "failed_applications": 0,
            "job_summaries": [],
        }

        for job in expired_jobs:
            job_id = str(job.get("jobid") or job.get("_id"))
            job_description = (job.get("description") or "").strip()
            job_skills = job.get("skills") or []
            self._log(f"Step 3: Processing job={job_id} title={job.get('title')}")

            applications = await self.job_applications.find(
                {
                    "job_id": job_id,
                    "$or": [
                        {"ai_score": {"$exists": False}},
                        {"ai_score": None},
                    ],
                }
            ).to_list(length=None)
            self._log(
                f"Step 4: Applications to screen for job={job_id} count={len(applications)}"
            )

            job_report = {
                "job_id": job_id,
                "title": job.get("title"),
                "applications_found": len(applications),
                "updated": 0,
                "failed": 0,
            }

            for application in applications:
                summary["processed_applications"] += 1
                self._log(
                    "Step 5: Screening application="
                    f"{application.get('_id')} candidate={application.get('candidate_id')}"
                )
                ok = await self._process_application(
                    application=application,
                    job_description=job_description,
                    job_skills=job_skills,
                    now=now,
                )
                if ok:
                    summary["updated_applications"] += 1
                    job_report["updated"] += 1
                    self._log(
                        f"Step 9: Application={application.get('_id')} updated successfully"
                    )
                else:
                    summary["failed_applications"] += 1
                    job_report["failed"] += 1
                    self._log(
                        f"Step 9: Application={application.get('_id')} failed during screening"
                    )

            await self.job_posts.update_one(
                {"_id": job["_id"]},
                {
                    "$set": {
                        "ai_screening_last_run_at": now,
                        "ai_screening_processed_count": job_report["updated"],
                        "ai_screening_failed_count": job_report["failed"],
                    }
                },
            )

            summary["processed_jobs"] += 1
            summary["job_summaries"].append(job_report)
            self._log(
                f"Step 10: Job={job_id} complete updated={job_report['updated']} failed={job_report['failed']}"
            )

        self._log(
            "Step 11: Run complete "
            f"processed_apps={summary['processed_applications']} "
            f"updated={summary['updated_applications']} failed={summary['failed_applications']}"
        )
        return summary

    async def _process_application(
        self,
        application: dict[str, Any],
        job_description: str,
        job_skills: list[str],
        now: datetime,
    ) -> bool:
        app_id = application.get("_id")
        resume_url = (application.get("resume_url") or "").strip()
        self._log(f"Step 6: Parsing resume for application={app_id} from {resume_url}")

        try:
            resume_text = await asyncio.to_thread(self.parser.parse, resume_url)
            if not resume_text:
                await self._mark_failure(app_id, "Resume text extraction failed")
                return False

            self._log(
                f"Step 6: Resume parsed for application={app_id}, chars={len(resume_text)}"
            )

            self._log(f"Step 7: Running AI analysis for application={app_id}")
            result = await asyncio.to_thread(
                self.agent.analyze_resume_text,
                resume_text,
                job_skills,
                job_description,
            )

            if not isinstance(result, dict) or result.get("error"):
                await self._mark_failure(app_id, result.get("error", "AI analysis failed"))
                return False

            score = result.get("overall_score")
            strengths = result.get("strengths") or []
            weaknesses = result.get("missing_skills") or []
            self._log(
                f"Step 7: AI output for application={app_id} score={score} "
                f"strengths={len(strengths)} weaknesses={len(weaknesses)}"
            )

            next_status = application.get("status")
            # Temporary: disable automatic rejection based on the screening cutoff.
            # if isinstance(score, (int, float)) and next_status in ("applied", "shortlisted"):
            #     next_status = "shortlisted" if score >= self.cutoff_score else "rejected"

            self._log(
                f"Step 8: Saving application={app_id} status={next_status} ai_score={score}"
            )
            await self.job_applications.update_one(
                {"_id": app_id},
                {
                    "$set": {
                        "ai_score": score,
                        "strengths": strengths,
                        "weaknesses": weaknesses,
                        "status": next_status,
                        "ai_screened_at": now,
                    },
                    "$unset": {
                        "ai_screening_error": "",
                    },
                },
            )
            return True
        except Exception as exc:
            await self._mark_failure(app_id, str(exc))
            return False

    async def _mark_failure(self, application_id: Any, reason: str) -> None:
        self._log(f"Step X: Failure application={application_id} reason={reason}")
        await self.job_applications.update_one(
            {"_id": application_id},
            {
                "$set": {
                    "ai_screening_error": reason,
                    "ai_screened_at": datetime.utcnow(),
                }
            },
        )


def build_pipeline_from_env(base_dir: str | Path) -> ScreeningPipeline | None:
    print("[ai-screening] Loading environment for AI pipeline", flush=True)
    root_env = Path(base_dir) / ".env"
    if root_env.exists():
        load_dotenv(root_env, override=False)

    load_dotenv(Path(base_dir) / "AI_Model" / ".env", override=False)
    load_dotenv(Path(base_dir) / "services" / "job-service" / ".env", override=False)
    load_dotenv(Path(base_dir) / "services" / "application-service" / ".env", override=False)

    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "ai_recruitment")

    # Accept common variants to avoid env naming mistakes during local setup.
    api_key = (
        os.getenv("OPENROUTER_API_KEY")
        or os.getenv("openrouter_api_key")
        or os.getenv("OPENROUTER_KEY")
        or os.getenv("openrouter_key")
        or ""
    ).strip()

    if not api_key:
        print("[ai-screening] OPENROUTER API key not found in environment", flush=True)
        return None

    cutoff_score = int(os.getenv("AI_CUTOFF_SCORE", "75"))

    return ScreeningPipeline(
        mongo_uri=mongo_uri,
        database_name=database_name,
        openrouter_api_key=api_key,
        base_dir=base_dir,
        cutoff_score=cutoff_score,
    )
