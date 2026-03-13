import asyncio
import sys
from datetime import datetime
from pathlib import Path

from database import get_db
from models.round import Round
from models.round_result import RoundResult, RoundResultStatus

# Make backend root importable so shared.email works when running this service standalone.
BACKEND_ROOT = Path(__file__).resolve().parents[3]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from shared.email import send_ai_application_result


async def _get_user_doc(candidate_id: str) -> dict | None:
    db = get_db()
    users = db["users"]
    return await users.find_one({"$expr": {"$eq": [{"$toString": "$_id"}, candidate_id]}})


async def _get_job_title(job_id: str) -> str:
    db = get_db()

    query = {"$expr": {"$eq": [{"$toString": "$_id"}, job_id]}}

    job_doc = await db["job_posts"].find_one(query)
    if job_doc and job_doc.get("title"):
        return str(job_doc["title"])

    fallback_job_doc = await db["jobs"].find_one(query)
    if fallback_job_doc and fallback_job_doc.get("title"):
        return str(fallback_job_doc["title"])

    return "the applied role"


async def process_expired_round_notifications() -> dict[str, int]:
    now = datetime.utcnow()

    expired_rounds = await Round.find(
        Round.end_time != None,
        Round.end_time <= now,
    ).to_list()
    expired_round_ids = {str(doc.id) for doc in expired_rounds}

    if not expired_round_ids:
        return {"expired_rounds": 0, "processed": 0, "sent": 0, "skipped": 0, "failed": 0}

    docs = await RoundResult.find(RoundResult.notification_sent_at == None).to_list()

    processed = 0
    sent = 0
    skipped = 0
    failed = 0

    for doc in docs:
        if doc.round_id not in expired_round_ids:
            continue
        if doc.status not in {
            RoundResultStatus.passed,
            RoundResultStatus.failed,
            RoundResultStatus.rejected,
        }:
            continue

        processed += 1

        try:
            db = get_db()
            application = await db["job_applications"].find_one(
                {"$expr": {"$eq": [{"$toString": "$_id"}, doc.application_id]}}
            )

            if not application:
                skipped += 1
                continue

            user_doc = await _get_user_doc(doc.candidate_id)
            email = (user_doc or {}).get("email")
            candidate_name = (user_doc or {}).get("name") or application.get("applicant_name")

            if not email:
                skipped += 1
                continue

            status = "accepted" if doc.status == RoundResultStatus.passed else "rejected"
            job_title = await _get_job_title(doc.job_id)

            await send_ai_application_result(
                to=str(email),
                candidate_name=str(candidate_name),
                job_title=job_title,
                status=status,
                matching_skills=application.get("strengths") or [],
                weaknesses=application.get("weaknesses") or [],
            )

            doc.notification_sent_at = now
            await doc.save()
            sent += 1

        except Exception:
            failed += 1

    return {
        "expired_rounds": len(expired_round_ids),
        "processed": processed,
        "sent": sent,
        "skipped": skipped,
        "failed": failed,
    }


async def round_email_cron_loop(interval_seconds: int) -> None:
    while True:
        try:
            summary = await process_expired_round_notifications()
            if summary["processed"] > 0:
                print(f"[application-service] round email cron summary: {summary}")
        except Exception as exc:
            print(f"[application-service] round email cron error: {exc}")

        await asyncio.sleep(interval_seconds)
