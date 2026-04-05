from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator


class ApplicationStatus(str, Enum):
    applied = "applied"
    shortlisted = "shortlisted"
    in_round = "in_round"
    selected = "selected"
    rejected = "rejected"


class PipelineSnapshotRoundSchema(BaseModel):
    round_id: str
    name: str
    order: int


class JobApplicationCreateSchema(BaseModel):
    """Request body for submitting a job application (non-file fields)."""

    job_id: str
    candidate_id: Optional[str] = None
    email: Optional[str] = None
    applicant_name: str
    address: str
    highest_qualification: str
    experience: str
    resume_url: str             # URL or stored path to the uploaded résumé
    ai_score: Optional[float] = None
    strengths: Optional[list[str]] = None
    weaknesses: Optional[list[str]] = None
    status: ApplicationStatus = ApplicationStatus.applied

    @field_validator(
        "job_id", "applicant_name", "address",
        "highest_qualification", "experience", "resume_url"
    )
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field must not be empty")
        return v.strip()


class JobApplicationUpdateSchema(BaseModel):
    """Request body for partially updating a job application (all fields optional)."""

    candidate_id: Optional[str] = None
    email: Optional[str] = None
    applicant_name: Optional[str] = None
    address: Optional[str] = None
    highest_qualification: Optional[str] = None
    experience: Optional[str] = None
    resume_url: Optional[str] = None
    ai_score: Optional[float] = None
    strengths: Optional[list[str]] = None
    weaknesses: Optional[list[str]] = None
    status: Optional[ApplicationStatus] = None


class JobApplicationResponseSchema(BaseModel):
    """Response body returned after submitting or fetching a job application."""

    id: str                         # serialised MongoDB _id  (j_d_id)
    job_id: str
    candidate_id: Optional[str] = None
    email: Optional[str] = None
    applicant_name: str
    address: str
    highest_qualification: str
    experience: str
    resume_url: str
    ai_score: Optional[float] = None
    strengths: list[str]
    weaknesses: list[str]
    pipeline_snapshot: list[PipelineSnapshotRoundSchema]
    current_round: Optional[int] = None
    submit_at: str                  # ISO-8601 string
    status: ApplicationStatus
