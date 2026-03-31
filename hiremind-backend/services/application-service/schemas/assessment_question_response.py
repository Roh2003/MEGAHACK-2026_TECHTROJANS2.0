from pydantic import AliasChoices, BaseModel, Field, field_validator


class CandidateQuestionAnswerItemSchema(BaseModel):
    question: str
    answer: list[str] = Field(default_factory=list)
    marks_obtained: int | None = None
    is_correct: bool | None = None

    @field_validator("question")
    @classmethod
    def normalize_question(cls, v: str) -> str:
        value = v.strip()
        if not value:
            raise ValueError("question must not be empty")
        return value

    @field_validator("marks_obtained")
    @classmethod
    def validate_marks_obtained(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("marks_obtained must be >= 0")
        return v


class AssessmentQuestionResponseCreateSchema(BaseModel):
    job_id: str = Field(validation_alias=AliasChoices("job_id", "jobId", "jobid"))
    round_id: str = Field(validation_alias=AliasChoices("round_id", "roundId", "roundid"))
    candidate_id: str = Field(
        validation_alias=AliasChoices("candidate_id", "candidateId", "candidateid")
    )
    totalmarks: int = 0
    questionanswer: list[CandidateQuestionAnswerItemSchema]

    @field_validator("job_id", "round_id", "candidate_id")
    @classmethod
    def not_empty(cls, v: str) -> str:
        value = v.strip()
        if not value:
            raise ValueError("Field must not be empty")
        return value

    @field_validator("totalmarks")
    @classmethod
    def validate_total_marks(cls, v: int) -> int:
        if v < 0:
            raise ValueError("totalmarks must be >= 0")
        return v


class AssessmentQuestionResponseSchema(BaseModel):
    id: str
    job_id: str
    round_id: str
    candidate_id: str
    totalmarks: int
    questionanswer: list[CandidateQuestionAnswerItemSchema]
    submitted_at: str
    updated_at: str
