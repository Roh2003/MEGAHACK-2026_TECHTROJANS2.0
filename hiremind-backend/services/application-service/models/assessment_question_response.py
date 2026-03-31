from datetime import datetime

from beanie import Document
from pydantic import BaseModel, Field


class CandidateQuestionAnswerItem(BaseModel):
    question: str
    answer: list[str] = Field(default_factory=list)
    marks_obtained: int | None = None
    is_correct: bool | None = None


class AssessmentQuestionResponse(Document):
    job_id: str
    round_id: str
    candidate_id: str
    totalmarks: int = 0
    questionanswer: list[CandidateQuestionAnswerItem] = Field(default_factory=list)
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "assessment_question_response"
        indexes = [
            "job_id",
            "round_id",
            "candidate_id",
            [("job_id", 1), ("round_id", 1), ("candidate_id", 1)],
        ]
