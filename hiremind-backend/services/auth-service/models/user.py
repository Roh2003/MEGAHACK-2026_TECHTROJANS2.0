from datetime import datetime
from typing import List, Optional

from beanie import Document, Link
from pydantic import Field

from models.organization import Organization


class User(Document):
    """
    MongoDB document model for a user.

    HR users carry organization_id (reference → Organization).
    Candidate users carry skills + experience.
    """

    name: str
    email: str
    password: str
    role: str                                   # "hr" | "candidate"
    phone_no: Optional[str] = None

    # HR-specific
    organization_id: Optional[Link[Organization]] = None       # ref → Organization._id (stored as str)

    # Candidate-specific
    skills: Optional[List[str]] = None
    experience: Optional[float] = None          # years of experience

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"

