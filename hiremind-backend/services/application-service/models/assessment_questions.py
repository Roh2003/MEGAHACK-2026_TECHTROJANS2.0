from datetime import datetime

from beanie import Document
from pydantic import BaseModel, Field


class AssessmentQuestionItem(BaseModel):
    question: str
    ans: list[str] = Field(default_factory=list)
    correctans: str | None = None
    marks: int = 0


class AssessmentQuestions(Document):
    job_id: str
    round_id: str
    questionans: list[AssessmentQuestionItem] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "assessment_questions"
        indexes = [
            "job_id",
            "round_id",
            [("job_id", 1), ("round_id", 1)],
        ]
