import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import HackathonStatus


class HackathonCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status: HackathonStatus = HackathonStatus.draft
    start_date: datetime | None = None
    end_date: datetime | None = None


class HackathonUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: HackathonStatus | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class HackathonStatusUpdate(BaseModel):
    status: HackathonStatus


class HackathonResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    status: HackathonStatus
    start_date: datetime | None
    end_date: datetime | None
    created_by: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class HackathonDetailResponse(HackathonResponse):
    teams_count: int
    criteria_count: int
