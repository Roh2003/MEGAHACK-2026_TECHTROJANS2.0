from datetime import datetime

from beanie import Document
from pydantic import Field


class Application(Document):
    """MongoDB document model for a job application."""

    job_id: str
    candidate_name: str
    email: str
    phone: str
    experience: str
    resume_path: str        # relative path under uploads/resumes/
    status: str = "pending" # pending | reviewed | accepted | rejected
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "applications"  # MongoDB collection name
