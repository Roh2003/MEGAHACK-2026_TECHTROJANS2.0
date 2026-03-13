from datetime import datetime
from enum import Enum

from beanie import Document
from pydantic import Field


class RoundResultStatus(str, Enum):
    pending = "PENDING"
    passed = "PASSED"
    failed = "FAILED"
    rejected = "REJECTED"


class RoundResult(Document):
    """Candidate performance for a specific round."""

    job_id: str
    application_id: str
    candidate_id: str
    round_id: str
    score: float | None = None
    status: RoundResultStatus
    feedback: str | None = None
    evaluated_by: str | None = None
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "round_results"
        indexes = [
            "application_id",
            "job_id",
            [("application_id", 1), ("round_id", 1)],
        ]
