from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator


class ApplicationStatus(str, Enum):
    pending = "pending"
    selected = "selected"
    rejected = "rejected"


class JobApplicationCreateSchema(BaseModel):
    """Request body for submitting a job application (non-file fields)."""

    job_id: str
    applicant_name: str
    address: str
    highest_qualification: str
    experience: str
    resume_url: str             # URL or stored path to the uploaded résumé

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

    applicant_name: Optional[str] = None
    address: Optional[str] = None
    highest_qualification: Optional[str] = None
    experience: Optional[str] = None
    resume_url: Optional[str] = None
    status: Optional[ApplicationStatus] = None


class JobApplicationResponseSchema(BaseModel):
    """Response body returned after submitting or fetching a job application."""

    id: str                         # serialised MongoDB _id  (j_d_id)
    job_id: str
    applicant_name: str
    address: str
    highest_qualification: str
    experience: str
    resume_url: str
    submit_at: str                  # ISO-8601 string
    status: ApplicationStatus
