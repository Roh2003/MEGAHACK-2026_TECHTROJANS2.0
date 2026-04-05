import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dotenv import load_dotenv

from models.assessment_question_response import AssessmentQuestionResponse
from models.assessment_questions import AssessmentQuestions
from models.job_application import JobApplication
from models.schedule_assessment import ScheduleAssessment
from models.round import Round
from models.round_result import RoundResult

load_dotenv()

MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME: str = os.getenv("DATABASE_NAME", "ai_recruitment")

_client: AsyncIOMotorClient = None


async def connect_db() -> None:
    global _client
    _client = AsyncIOMotorClient(MONGO_URI)
    await init_beanie(
        database=_client[DATABASE_NAME],
        document_models=[
            JobApplication,
            Round,
            RoundResult,
            AssessmentQuestions,
            AssessmentQuestionResponse,
            ScheduleAssessment,
        ],
    )
    print(f"[application-service] Connected to MongoDB — db: {DATABASE_NAME}")


def get_db():
    if _client is None:
        raise RuntimeError("Database is not connected")
    return _client[DATABASE_NAME]


async def close_db() -> None:
    global _client
    if _client:
        _client.close()
        print("[application-service] Disconnected from MongoDB")
