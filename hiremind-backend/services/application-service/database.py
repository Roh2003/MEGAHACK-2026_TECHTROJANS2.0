import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dotenv import load_dotenv

from models.application import Application
from models.job_application import JobApplication

load_dotenv()

MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME: str = os.getenv("DATABASE_NAME", "ai_recruitment")

_client: AsyncIOMotorClient = None


async def connect_db() -> None:
    global _client
    _client = AsyncIOMotorClient(MONGO_URI)
    await init_beanie(database=_client[DATABASE_NAME], document_models=[Application, JobApplication])
    print(f"[application-service] Connected to MongoDB — db: {DATABASE_NAME}")


async def close_db() -> None:
    global _client
    if _client:
        _client.close()
        print("[application-service] Disconnected from MongoDB")
