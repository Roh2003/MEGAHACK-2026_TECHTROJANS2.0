from pydantic import BaseModel, field_validator

from models.round_result import RoundResultStatus


class RoundResultCreateSchema(BaseModel):
    job_id: str
    application_id: str
    candidate_id: str
    round_id: str
    score: float | None = None
    status: RoundResultStatus
    feedback: str | None = None
    evaluated_by: str | None = None

    @field_validator("job_id", "application_id", "candidate_id", "round_id")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field must not be empty")
        return v.strip()

    @field_validator("feedback", "evaluated_by")
    @classmethod
    def normalize_optional_text(cls, v: str | None) -> str | None:
        if v is None:
            return None
        value = v.strip()
        return value or None


class RoundResultResponseSchema(BaseModel):
    id: str
    job_id: str
    application_id: str
    candidate_id: str
    round_id: str
    score: float | None = None
    status: RoundResultStatus
    feedback: str | None = None
    evaluated_by: str | None = None
    evaluated_at: str


class RoundCandidateDecisionSchema(BaseModel):
    job_id: str
    application_id: str
    candidate_id: str
    round_id: str
    score: float | None = None
    feedback: str | None = None
    evaluated_by: str | None = None

    @field_validator("job_id", "application_id", "candidate_id", "round_id")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field must not be empty")
        return v.strip()

    @field_validator("feedback", "evaluated_by")
    @classmethod
    def normalize_optional_text(cls, v: str | None) -> str | None:
        if v is None:
            return None
        value = v.strip()
        return value or None


class RoundWiseCandidateSchema(BaseModel):
    round_result_id: str
    job_id: str
    round_id: str
    application_id: str
    candidate_id: str
    candidate_name: str | None = None
    score: float | None = None
    status: RoundResultStatus
    feedback: str | None = None
    evaluated_by: str | None = None
    evaluated_at: str
