import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import CheckStatus, CheckType, SubmissionStatus


class ScoreCreate(BaseModel):
    criterion_id: uuid.UUID
    score: int = Field(ge=0, le=10)
    comment: str | None = None


class ScoreUpdate(BaseModel):
    score: int = Field(ge=0, le=10)
    comment: str | None = None


class ExpertScoreResponse(BaseModel):
    id: uuid.UUID
    submission_id: uuid.UUID
    criterion_id: uuid.UUID
    jury_id: uuid.UUID
    score: int
    comment: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AutoCheckSummary(BaseModel):
    check_type: CheckType
    status: CheckStatus
    score: float | None


class AIReviewResponse(BaseModel):
    model_name: str
    model_version: str
    score: float
    confidence: float
    verdict: str
    summary: str
    strengths: list[str]
    risks: list[str]
    missing_parts: list[str]
    jury_questions: list[str]
    feature_weights: dict[str, float]
    signals: dict[str, float]


class ReviewSubmissionSummary(BaseModel):
    submission_id: uuid.UUID
    team_id: uuid.UUID
    team_name: str
    status: SubmissionStatus
    auto_score: float | None
    my_score: float | None
    checks: list[AutoCheckSummary]


class ReviewDetailResponse(ReviewSubmissionSummary):
    repo_url: str | None
    repo_archive: str | None
    doc_file: str | None
    presentation: str | None
    screencast_file: str | None
    screencast_url: str | None
    ai_review: AIReviewResponse
    my_scores: list[ExpertScoreResponse]


class LeaderboardRow(BaseModel):
    rank: int
    team_id: uuid.UUID
    team_name: str
    auto_scores: dict[str, float | None]
    expert_scores: list[dict[str, float | int | str | None]]
    total_score: float
