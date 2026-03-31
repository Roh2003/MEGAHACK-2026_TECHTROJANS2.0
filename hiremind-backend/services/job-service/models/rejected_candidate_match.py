from datetime import datetime

from beanie import Document
from pydantic import Field


class RejectedCandidateMatch(Document):
    job_id: str
    source_application_id: str
    source_job_id: str
    candidate_id: str | None = None
    applicant_name: str
    address: str
    highest_qualification: str
    experience: str
    resume_url: str
    previous_ai_score: float | None = None
    matched_ai_score: float
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    source_status: str = "rejected"
    submit_at: datetime | None = None
    matched_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "rejected_candidate_matches"
        indexes = [
            "job_id",
            "candidate_id",
            "source_application_id",
            [("job_id", 1), ("candidate_id", 1)],
            [("job_id", 1), ("matched_ai_score", -1)],
        ]
