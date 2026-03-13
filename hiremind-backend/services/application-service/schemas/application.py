from pydantic import BaseModel, EmailStr, field_validator


class ApplicationCreateSchema(BaseModel):
    candidate_name: str
    email: EmailStr
    phone: str
    experience: str

    @field_validator("candidate_name", "phone", "experience")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field must not be empty")
        return v.strip()


class ApplicationResponseSchema(BaseModel):
    id: str
    job_id: str
    candidate_name: str
    email: str
    phone: str
    experience: str
    resume_path: str
    status: str
    created_at: str
