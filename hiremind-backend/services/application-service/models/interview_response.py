from datetime import datetime

from beanie import Document
from pydantic import BaseModel, Field


class ConversationTurn(BaseModel):
    speaker: str
    message: str
    timestamp: str | None = None


class InterviewResponse(Document):
    """Candidate interview response / interviewer feedback for a specific round."""

    job_id: str
    round_id: str
    candidate_id: str
    conversation: list[ConversationTurn] = Field(default_factory=list)
    speaking_fluency: float
    confidence_score: float
    answer_correctness_score: float
    overall_score: float
    candidate_summary: str
    detailed_summary: str
    strengths: list[str] = Field(default_factory=list)
    improvement_areas: list[str] = Field(default_factory=list)
    ai_model_used: str | None = None
    interviewed_by: str | None = None
    feedback: str | None = None
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "interview_responses"
        indexes = [
            "job_id",
            "round_id",
            "candidate_id",
            [("job_id", 1), ("round_id", 1), ("candidate_id", 1)],
        ]
