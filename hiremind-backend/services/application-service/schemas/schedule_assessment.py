from datetime import datetime
from typing import List

from pydantic import BaseModel, field_validator


class ScheduleAssessmentCreateSchema(BaseModel):
    job_id: str
    round_id: str
    assign_candidate_ids: List[str]
    assessment_description: str | None = None
    start_time: datetime
    end_time: datetime

    @field_validator("job_id", "round_id")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field must not be empty")
        return v.strip()

    @field_validator("assign_candidate_ids")
    @classmethod
    def candidates_not_empty(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("assign_candidate_ids must contain at least one candidate ID")
        return v

    @field_validator("end_time")
    @classmethod
    def end_after_start(cls, v: datetime, info) -> datetime:
        start = info.data.get("start_time")
        if start and v <= start:
            raise ValueError("end_time must be after start_time")
        return v


class ScheduleAssessmentResponseSchema(BaseModel):
    id: str
    assessment_id: str
    job_id: str
    round_id: str
    assign_candidate_ids: List[str]
    assessment_description: str | None = None
    assessment_link: str
    start_time: str
    end_time: str
    created_at: str
