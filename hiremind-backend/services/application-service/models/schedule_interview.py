import uuid
from datetime import datetime
from typing import List

from beanie import Document
from pydantic import Field


class ScheduleInterview(Document):
    """Scheduled interview session for a specific round, assigned to a set of candidates."""

    interview_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    round_id: str
    assign_candidate_ids: List[str] = Field(default_factory=list)
    schedule_done: bool = False
    interview_description: str | None = None
    interview_link: str
    start_time: datetime
    end_time: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "schedule_interview"
        indexes = [
            "job_id",
            "round_id",
            "interview_id",
        ]
