from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator, model_validator


class JobPostCreateSchema(BaseModel):
    """Request body for creating a new job post."""

    title: str
    description: str
    skills: List[str]
    experience: str
    location: str
    ctc: str
    start_time: datetime
    end_time: datetime

    @field_validator("title", "description", "experience", "location", "ctc")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field must not be empty")
        return v.strip()

    @field_validator("skills")
    @classmethod
    def skills_not_empty(cls, v: List[str]) -> List[str]:
        cleaned = [s.strip() for s in v if s.strip()]
        if not cleaned:
            raise ValueError("At least one skill is required")
        return cleaned

    @model_validator(mode="after")
    def end_after_start(self) -> "JobPostCreateSchema":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class JobPostUpdateSchema(BaseModel):
    """Request body for partially updating a job post (all fields optional)."""

    title: Optional[str] = None
    description: Optional[str] = None
    skills: Optional[List[str]] = None
    experience: Optional[str] = None
    location: Optional[str] = None
    ctc: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @model_validator(mode="after")
    def end_after_start_if_both_provided(self) -> "JobPostUpdateSchema":
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class JobPostResponseSchema(BaseModel):
    """Response body returned after creating or fetching a job post."""

    id: str
    title: str
    description: str
    skills: List[str]
    experience: str
    location: str
    ctc: str
    start_time: str             # ISO-8601 string
    end_time: str               # ISO-8601 string
    created_by: str
    created_at: str             # ISO-8601 string


class RejectedCandidateMatchResponseSchema(BaseModel):
    id: str
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
    strengths: List[str]
    weaknesses: List[str]
    source_status: str
    submit_at: str | None = None
    matched_at: str
    updated_at: str


class JobRejectedCandidateRematchSummarySchema(BaseModel):
    enabled: bool
    scanned_rejected_applications: int
    matched_candidates: int
    top_candidate: RejectedCandidateMatchResponseSchema | None = None
    top_candidates: List[RejectedCandidateMatchResponseSchema] = []


class JobPostCreateWithMatchesResponseSchema(JobPostResponseSchema):
    rejected_candidate_rematch: JobRejectedCandidateRematchSummarySchema
