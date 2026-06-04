import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.models.enums import CheckStatus, CheckType, SubmissionStatus


class SubmissionCreate(BaseModel):
    team_id: uuid.UUID
    hackathon_id: uuid.UUID


class CheckResultResponse(BaseModel):
    id: uuid.UUID
    submission_id: uuid.UUID
    check_type: CheckType
    status: CheckStatus
    score: float | None
    report: dict[str, Any] | None
    started_at: datetime | None
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class SubmissionResponse(BaseModel):
    id: uuid.UUID
    team_id: uuid.UUID
    hackathon_id: uuid.UUID
    repo_url: str | None
    repo_archive: str | None
    doc_file: str | None
    presentation: str | None
    screencast_file: str | None
    screencast_url: str | None
    status: SubmissionStatus
    submitted_at: datetime | None
    updated_at: datetime
    check_results: list[CheckResultResponse] = []

    model_config = {"from_attributes": True}
