import csv
import io
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.check_result import CheckResult
from app.models.criterion import Criterion
from app.models.expert_score import ExpertScore
from app.models.submission import Submission
from app.models.team import Team
from app.models.user import User
from app.schemas.score import (
    AutoCheckSummary,
    ExpertScoreResponse,
    LeaderboardRow,
    ReviewDetailResponse,
    ReviewSubmissionSummary,
    ScoreCreate,
    ScoreUpdate,
)
from app.services.hackathon_service import get_hackathon


async def list_review_submissions(db: AsyncSession, hackathon_id: UUID, jury: User) -> list[ReviewSubmissionSummary]:
    await get_hackathon(db, hackathon_id)
    result = await db.execute(
        select(Submission)
        .where(Submission.hackathon_id == hackathon_id)
        .options(
            selectinload(Submission.team),
            selectinload(Submission.check_results),
            selectinload(Submission.expert_scores),
        )
    )
    return [build_review_summary(submission, jury.id) for submission in result.scalars().all()]


async def get_review_detail(db: AsyncSession, submission_id: UUID, jury: User) -> ReviewDetailResponse:
    submission = await get_submission_with_related(db, submission_id)
    summary = build_review_summary(submission, jury.id)
    my_scores = [score for score in submission.expert_scores if score.jury_id == jury.id]
    return ReviewDetailResponse(
        **summary.model_dump(),
        repo_url=submission.repo_url,
        repo_archive=submission.repo_archive,
        doc_file=submission.doc_file,
        presentation=submission.presentation,
        screencast_file=submission.screencast_file,
        screencast_url=submission.screencast_url,
        my_scores=[ExpertScoreResponse.model_validate(score) for score in my_scores],
    )


async def get_submission_with_related(db: AsyncSession, submission_id: UUID) -> Submission:
    result = await db.execute(
        select(Submission)
        .where(Submission.id == submission_id)
        .options(
            selectinload(Submission.team),
            selectinload(Submission.check_results),
            selectinload(Submission.expert_scores),
        )
    )
    submission = result.scalar_one_or_none()
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    return submission


def build_review_summary(submission: Submission, jury_id: UUID) -> ReviewSubmissionSummary:
    completed_scores = [check.score for check in submission.check_results if check.score is not None]
    my_scores = [score.score for score in submission.expert_scores if score.jury_id == jury_id]
    return ReviewSubmissionSummary(
        submission_id=submission.id,
        team_id=submission.team_id,
        team_name=submission.team.name,
        status=submission.status,
        auto_score=round(sum(completed_scores) / len(completed_scores), 2) if completed_scores else None,
        my_score=round(sum(my_scores) / len(my_scores), 2) if my_scores else None,
        checks=[
            AutoCheckSummary(check_type=check.check_type, status=check.status, score=check.score)
            for check in submission.check_results
        ],
    )


async def upsert_scores(
    db: AsyncSession,
    submission_id: UUID,
    payload: list[ScoreCreate],
    jury: User,
) -> list[ExpertScore]:
    submission = await get_submission_with_related(db, submission_id)
    criteria = await get_criteria_map(db, submission.hackathon_id)

    existing_result = await db.execute(
        select(ExpertScore).where(ExpertScore.submission_id == submission_id, ExpertScore.jury_id == jury.id)
    )
    existing = {(score.criterion_id, score.jury_id): score for score in existing_result.scalars().all()}
    saved: list[ExpertScore] = []

    for item in payload:
        criterion = criteria.get(item.criterion_id)
        if criterion is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Criterion not found in hackathon")
        if item.score > criterion.max_score:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Score exceeds criterion max_score")

        score = existing.get((item.criterion_id, jury.id))
        if score is None:
            score = ExpertScore(
                submission_id=submission_id,
                criterion_id=item.criterion_id,
                jury_id=jury.id,
                score=item.score,
                comment=item.comment,
            )
            db.add(score)
        else:
            score.score = item.score
            score.comment = item.comment
        saved.append(score)

    await db.commit()
    for score in saved:
        await db.refresh(score)
    return saved


async def update_score(db: AsyncSession, score_id: UUID, payload: ScoreUpdate, jury: User) -> ExpertScore:
    score = await db.get(ExpertScore, score_id)
    if score is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Score not found")
    if score.jury_id != jury.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only score owner can update score")

    criterion = await db.get(Criterion, score.criterion_id)
    if criterion is not None and payload.score > criterion.max_score:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Score exceeds criterion max_score")

    score.score = payload.score
    score.comment = payload.comment
    await db.commit()
    await db.refresh(score)
    return score


async def get_criteria_map(db: AsyncSession, hackathon_id: UUID) -> dict[UUID, Criterion]:
    result = await db.execute(select(Criterion).where(Criterion.hackathon_id == hackathon_id))
    return {criterion.id: criterion for criterion in result.scalars().all()}


def auto_score_for_criterion(criterion: Criterion, checks: list[CheckResult]) -> float | None:
    if not checks:
        return None

    name = criterion.name.lower()
    targets = []
    if any(token in name for token in ["док", "doc"]):
        targets = ["documentation"]
    elif any(token in name for token in ["през", "presentation"]):
        targets = ["presentation"]
    elif any(token in name for token in ["скрин", "video", "screencast"]):
        targets = ["screencast"]
    elif any(token in name for token in ["код", "code", "архитект"]):
        targets = ["code"]

    selected = [check.score for check in checks if check.score is not None and (not targets or check.check_type in targets)]
    if not selected:
        return None
    return round(sum(selected) / len(selected), 2)


async def calculate_team_score(db: AsyncSession, team_id: UUID, hackathon_id: UUID) -> LeaderboardRow:
    criteria = list((await get_criteria_map(db, hackathon_id)).values())
    submission_result = await db.execute(
        select(Submission)
        .where(Submission.team_id == team_id, Submission.hackathon_id == hackathon_id)
        .options(selectinload(Submission.check_results), selectinload(Submission.expert_scores), selectinload(Submission.team))
    )
    submission = submission_result.scalar_one_or_none()
    team = await db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    if submission is None:
        return LeaderboardRow(rank=0, team_id=team.id, team_name=team.name, auto_scores={}, expert_scores=[], total_score=0.0)

    total = 0.0
    auto_scores: dict[str, float | None] = {}
    expert_scores: list[dict[str, float | int | str | None]] = []

    for criterion in criteria:
        if criterion.is_auto:
            score = auto_score_for_criterion(criterion, submission.check_results)
            auto_scores[criterion.name] = score
            total += (score or 0.0) * criterion.weight
        else:
            scores = [score.score for score in submission.expert_scores if score.criterion_id == criterion.id]
            avg_score = round(sum(scores) / len(scores), 2) if scores else None
            expert_scores.append(
                {
                    "criterion": criterion.name,
                    "avg_score": avg_score,
                    "jury_count": len(scores),
                }
            )
            total += (avg_score or 0.0) * criterion.weight

    return LeaderboardRow(
        rank=0,
        team_id=team.id,
        team_name=team.name,
        auto_scores=auto_scores,
        expert_scores=expert_scores,
        total_score=round(total, 2),
    )


async def get_leaderboard(db: AsyncSession, hackathon_id: UUID) -> list[LeaderboardRow]:
    await get_hackathon(db, hackathon_id)
    result = await db.execute(select(Team).where(Team.hackathon_id == hackathon_id))
    rows = [await calculate_team_score(db, team.id, hackathon_id) for team in result.scalars().all()]
    rows.sort(key=lambda row: row.total_score, reverse=True)
    for index, row in enumerate(rows, start=1):
        row.rank = index
    return rows


def leaderboard_to_csv(rows: list[LeaderboardRow]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["rank", "team_id", "team_name", "total_score"])
    for row in rows:
        writer.writerow([row.rank, row.team_id, row.team_name, row.total_score])
    return output.getvalue()
