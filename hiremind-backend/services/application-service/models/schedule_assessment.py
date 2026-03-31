import uuid
from datetime import datetime
from typing import List

from beanie import Document
from pydantic import Field


class ScheduleAssessment(Document):
    """Scheduled assessment session for a specific round, assigned to candidates."""

    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    round_id: str
    assign_candidate_ids: List[str] = Field(default_factory=list)
    assessment_description: str | None = None
    assessment_link: str
    start_time: datetime
    end_time: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "schedule_assessment"
        indexes = [
            "job_id",
            "round_id",
            "assessment_id",
        ]
