from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import Field
from pymongo import IndexModel


class Organization(Document):
    """
    MongoDB document model for an organization.

    Collection: organizations
    HR users reference this via organization_id.
    """

    organization_id: str | None = Field(default=None)
    name: str
    industry: str
    size: Optional[int] = None          # headcount
    location: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "organizations"
        indexes = [
            IndexModel([("organization_id", 1)], unique=True, sparse=True),
        ]
