from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ConversationTurnSchema(BaseModel):
    speaker: str
    message: str
    timestamp: Optional[str] = None

    @field_validator("speaker", "message")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field must not be empty")
        return v.strip()


class InterviewResponseCreateSchema(BaseModel):
    job_id: str
    round_id: str
    candidate_id: str
    conversation: list[ConversationTurnSchema] = Field(default_factory=list)
    speaking_fluency: float
    confidence_score: float
    answer_correctness_score: float
    interviewed_by: Optional[str] = None
    feedback: Optional[str] = None

    @field_validator("job_id", "round_id", "candidate_id")
    @classmethod
    def ids_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field must not be empty")
        return v.strip()

    @field_validator("speaking_fluency", "confidence_score", "answer_correctness_score")
    @classmethod
    def score_range(cls, v: float) -> float:
        if v < 0 or v > 100:
            raise ValueError("Score must be between 0 and 100")
        return float(v)


class InterviewResponseSchema(BaseModel):
    id: str
    job_id: str
    round_id: str
    candidate_id: str
    conversation: list[ConversationTurnSchema]
    speaking_fluency: float
    confidence_score: float
    answer_correctness_score: float
    overall_score: float
    candidate_summary: str
    detailed_summary: str
    strengths: list[str]
    improvement_areas: list[str]
    ai_model_used: Optional[str] = None
    interviewed_by: Optional[str] = None
    feedback: Optional[str] = None
    submitted_at: str
    updated_at: str
