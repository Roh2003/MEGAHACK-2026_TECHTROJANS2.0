from datetime import datetime
from enum import Enum

from beanie import Document
from pydantic import BaseModel, Field


class ApplicationStatus(str, Enum):
    applied = "applied"
    shortlisted = "shortlisted"
    in_round = "in_round"
    selected = "selected"
    rejected = "rejected"


class PipelineSnapshotRound(BaseModel):
    round_id: str
    name: str
    order: int


class JobApplication(Document):
    """
    MongoDB document model for a job application.

    Collection: job_applications
    j_d_id  — unique job-description / application reference ID (stored as _id)
    job_id  — references JobPost.jobid  (logical FK; MongoDB does not enforce referential integrity)
    """

    job_id: str                                            # FK → JobPost.jobid
    candidate_id: str | None = None                        # FK → User._id
    email: str | None = None
    applicant_name: str
    address: str
    highest_qualification: str
    experience: str                                        # e.g. "3 years", "Fresher"
    resume_url: str                                       # URL or file path to résumé
    ai_score: float | None = None
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    pipeline_snapshot: list[PipelineSnapshotRound] = Field(default_factory=list)
    current_round: int | None = None
    submit_at: datetime = Field(default_factory=datetime.utcnow)
    status: ApplicationStatus = ApplicationStatus.applied

    class Settings:
        name = "job_applications"                          # MongoDB collection name
        indexes = [
            "job_id",
            "candidate_id",
        ]
