from datetime import datetime
from enum import Enum

from beanie import Document
from pydantic import Field


class RoundType(str, Enum):
    assessment = "ASSESSMENT"
    interview = "INTERVIEW"
    screening = "SCREENING"
    other = "OTHER"


class Round(Document):
    """Round definition for a specific job pipeline."""

    job_id: str
    round_name: str
    round_order: int
    type: RoundType = RoundType.other
    max_score: float | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "rounds"
        indexes = [
            "job_id",
            [("job_id", 1), ("round_order", 1)],
        ]
