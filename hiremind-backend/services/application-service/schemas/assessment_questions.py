from pydantic import AliasChoices, BaseModel, Field, field_validator


class AssessmentQuestionItemSchema(BaseModel):
    question: str
    ans: list[str] = Field(default_factory=list)
    correctans: str | None = None
    marks: int = 0

    @field_validator("question")
    @classmethod
    def normalize_question(cls, v: str) -> str:
        value = v.strip()
        if not value:
            raise ValueError("question must not be empty")
        return value

    @field_validator("correctans")
    @classmethod
    def normalize_correct_answer(cls, v: str | None) -> str | None:
        if v is None:
            return None
        value = v.strip()
        return value or None

    @field_validator("marks")
    @classmethod
    def validate_marks(cls, v: int) -> int:
        if v < 0:
            raise ValueError("marks must be >= 0")
        return v


class AssessmentQuestionsCreateSchema(BaseModel):
    job_id: str = Field(validation_alias=AliasChoices("job_id", "jobId", "jobid"))
    round_id: str = Field(validation_alias=AliasChoices("round_id", "roundId", "roundid"))
    questionans: list[AssessmentQuestionItemSchema]

    @field_validator("job_id", "round_id")
    @classmethod
    def not_empty(cls, v: str) -> str:
        value = v.strip()
        if not value:
            raise ValueError("Field must not be empty")
        return value


class AssessmentQuestionsResponseSchema(BaseModel):
    id: str
    job_id: str
    round_id: str
    questionans: list[AssessmentQuestionItemSchema]
    created_at: str
    updated_at: str
