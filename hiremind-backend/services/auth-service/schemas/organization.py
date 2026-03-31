from typing import Optional
from pydantic import BaseModel, field_validator


class OrganizationCreateSchema(BaseModel):
    name: str
    industry: str
    size: Optional[int] = None
    location: str

    @field_validator("name", "industry", "location")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field must not be empty")
        return v.strip()


class OrganizationUpdateSchema(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[int] = None
    location: Optional[str] = None


class OrganizationResponseSchema(BaseModel):
    id: str
    organization_id: str
    name: str
    industry: str
    size: Optional[int]
    location: str
    created_at: str
