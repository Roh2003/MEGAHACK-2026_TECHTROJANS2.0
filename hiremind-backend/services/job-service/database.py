import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dotenv import load_dotenv

from models.job_post import JobPost
from models.rejected_candidate_match import RejectedCandidateMatch
from services.job_service import backfill_missing_jobids

load_dotenv()

MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME: str = os.getenv("DATABASE_NAME", "ai_recruitment")

_client: AsyncIOMotorClient = None


async def connect_db() -> None:
    global _client
    _client = AsyncIOMotorClient(MONGO_URI)
    await init_beanie(
        database=_client[DATABASE_NAME],
        document_models=[JobPost, RejectedCandidateMatch],
    )
    backfilled = await backfill_missing_jobids()
    if backfilled:
        print(f"[job-service] Backfilled {backfilled} legacy job records with public jobid values")
    print(f"[job-service] Connected to MongoDB — db: {DATABASE_NAME}")


async def close_db() -> None:
    global _client
    if _client:
        _client.close()
        print("[job-service] Disconnected from MongoDB")
