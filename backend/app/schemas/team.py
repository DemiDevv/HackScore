import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import UserRole


class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class TeamMemberAdd(BaseModel):
    email: str = Field(min_length=3, max_length=255)


class TeamMemberResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    email: str
    full_name: str
    role: UserRole
    is_captain: bool


class TeamResponse(BaseModel):
    id: uuid.UUID
    name: str
    hackathon_id: uuid.UUID
    created_at: datetime
    members: list[TeamMemberResponse] = []

    model_config = {"from_attributes": True}
