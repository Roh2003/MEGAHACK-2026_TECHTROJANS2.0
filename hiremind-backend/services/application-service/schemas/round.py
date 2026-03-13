from datetime import datetime

from pydantic import BaseModel, field_validator

from models.round import RoundType


class RoundCreateSchema(BaseModel):
    job_id: str
    round_name: str
    round_order: int
    type: RoundType = RoundType.other
    max_score: float | None = None

    @field_validator("job_id", "round_name")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field must not be empty")
        return v.strip()

    @field_validator("round_order")
    @classmethod
    def valid_order(cls, v: int) -> int:
        if v < 1:
            raise ValueError("round_order must be >= 1")
        return v

    @field_validator("max_score")
    @classmethod
    def valid_max_score(cls, v: float | None) -> float | None:
        if v is not None and v <= 0:
            raise ValueError("max_score must be > 0")
        return v


class RoundResponseSchema(BaseModel):
    id: str
    job_id: str
    round_name: str
    round_order: int
    type: RoundType
    max_score: float | None = None
    created_at: str
