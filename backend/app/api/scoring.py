from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import UserRole
from app.models.user import User
from app.schemas.score import (
    ExpertScoreResponse,
    LeaderboardRow,
    ReviewDetailResponse,
    ReviewSubmissionSummary,
    ScoreCreate,
    ScoreUpdate,
)
from app.services import scoring_service
from app.utils.deps import get_db, require_role


router = APIRouter(prefix="/scoring", tags=["scoring"])


@router.get("/hackathons/{hackathon_id}/submissions", response_model=list[ReviewSubmissionSummary])
async def list_review_submissions(
    hackathon_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.jury))],
) -> list[ReviewSubmissionSummary]:
    return await scoring_service.list_review_submissions(db, hackathon_id, current_user)


@router.get("/submissions/{submission_id}/review", response_model=ReviewDetailResponse)
async def get_review_detail(
    submission_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.jury))],
) -> ReviewDetailResponse:
    return await scoring_service.get_review_detail(db, submission_id, current_user)


@router.post("/submissions/{submission_id}/scores", response_model=list[ExpertScoreResponse])
async def save_scores(
    submission_id: UUID,
    payload: list[ScoreCreate],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.jury))],
) -> list[ExpertScoreResponse]:
    scores = await scoring_service.upsert_scores(db, submission_id, payload, current_user)
    return [ExpertScoreResponse.model_validate(score) for score in scores]


@router.put("/scores/{score_id}", response_model=ExpertScoreResponse)
async def update_score(
    score_id: UUID,
    payload: ScoreUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.jury))],
) -> ExpertScoreResponse:
    score = await scoring_service.update_score(db, score_id, payload, current_user)
    return ExpertScoreResponse.model_validate(score)


@router.get("/hackathons/{hackathon_id}/leaderboard", response_model=list[LeaderboardRow])
async def get_leaderboard(
    hackathon_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_role(UserRole.organizer))],
) -> list[LeaderboardRow]:
    return await scoring_service.get_leaderboard(db, hackathon_id)


@router.get("/hackathons/{hackathon_id}/leaderboard/export")
async def export_leaderboard(
    hackathon_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_role(UserRole.organizer))],
) -> Response:
    rows = await scoring_service.get_leaderboard(db, hackathon_id)
    csv_body = scoring_service.leaderboard_to_csv(rows)
    return Response(
        content=csv_body,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leaderboard.csv"},
    )
