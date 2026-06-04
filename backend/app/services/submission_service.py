from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.check_result import CheckResult
from app.models.enums import CheckStatus, CheckType, SubmissionStatus, UserRole
from app.models.submission import Submission
from app.models.team import TeamMember
from app.models.user import User
from app.schemas.submission import SubmissionCreate
from app.services.hackathon_service import get_hackathon
from app.services.team_service import ensure_team_in_hackathon, get_team
from app.utils.file_handler import save_upload
from app.workers.code_analyzer import analyze_code
from app.workers.doc_validator import validate_documentation
from app.workers.presentation_checker import check_presentation
from app.workers.video_processor import process_video


async def get_submission(db: AsyncSession, submission_id: UUID) -> Submission:
    result = await db.execute(
        select(Submission)
        .where(Submission.id == submission_id)
        .options(selectinload(Submission.check_results))
    )
    submission = result.scalar_one_or_none()
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    return submission


async def ensure_team_member(db: AsyncSession, team_id: UUID, user: User) -> None:
    result = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == user.id)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a member of this team")


async def ensure_can_view_submission(db: AsyncSession, submission: Submission, user: User) -> None:
    if user.role == UserRole.participant:
        await ensure_team_member(db, submission.team_id, user)


async def ensure_can_edit_submission(db: AsyncSession, submission: Submission, user: User) -> None:
    if user.role != UserRole.participant:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only participants can edit submissions")
    await ensure_team_member(db, submission.team_id, user)


async def create_submission(db: AsyncSession, payload: SubmissionCreate, user: User) -> Submission:
    team = await get_team(db, payload.team_id)
    ensure_team_in_hackathon(team, payload.hackathon_id)
    await get_hackathon(db, payload.hackathon_id)
    await ensure_team_member(db, payload.team_id, user)

    existing = await db.execute(
        select(Submission).where(
            Submission.team_id == payload.team_id,
            Submission.hackathon_id == payload.hackathon_id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Submission already exists for team")

    submission = Submission(team_id=payload.team_id, hackathon_id=payload.hackathon_id)
    db.add(submission)
    await db.commit()
    return await get_submission(db, submission.id)


async def get_submission_for_user(db: AsyncSession, submission_id: UUID, user: User) -> Submission:
    submission = await get_submission(db, submission_id)
    await ensure_can_view_submission(db, submission, user)
    return submission


async def get_submission_by_team(db: AsyncSession, team_id: UUID, user: User) -> Submission:
    if user.role == UserRole.participant:
        await ensure_team_member(db, team_id, user)

    result = await db.execute(
        select(Submission)
        .where(Submission.team_id == team_id)
        .options(selectinload(Submission.check_results))
    )
    submission = result.scalar_one_or_none()
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    return submission


async def update_repo(
    db: AsyncSession,
    submission_id: UUID,
    user: User,
    repo_url: str | None,
    repo_archive: UploadFile | None,
) -> Submission:
    submission = await get_submission(db, submission_id)
    await ensure_can_edit_submission(db, submission, user)

    if not repo_url and repo_archive is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="repo_url or repo_archive is required")

    if repo_url:
        submission.repo_url = repo_url.strip()
        submission.repo_archive = None

    if repo_archive is not None:
        submission.repo_archive = await save_upload(repo_archive, f"{submission.id}/repo", "archive")
        submission.repo_url = None

    await db.commit()
    return await get_submission(db, submission.id)


async def update_documentation(
    db: AsyncSession,
    submission_id: UUID,
    user: User,
    file: UploadFile,
) -> Submission:
    submission = await get_submission(db, submission_id)
    await ensure_can_edit_submission(db, submission, user)
    submission.doc_file = await save_upload(file, f"{submission.id}/documentation", "documentation")
    await db.commit()
    return await get_submission(db, submission.id)


async def update_presentation(
    db: AsyncSession,
    submission_id: UUID,
    user: User,
    file: UploadFile,
) -> Submission:
    submission = await get_submission(db, submission_id)
    await ensure_can_edit_submission(db, submission, user)
    submission.presentation = await save_upload(file, f"{submission.id}/presentation", "presentation")
    await db.commit()
    return await get_submission(db, submission.id)


async def update_screencast(
    db: AsyncSession,
    submission_id: UUID,
    user: User,
    screencast_url: str | None,
    file: UploadFile | None,
) -> Submission:
    submission = await get_submission(db, submission_id)
    await ensure_can_edit_submission(db, submission, user)

    if not screencast_url and file is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="screencast_url or file is required")

    if screencast_url:
        submission.screencast_url = screencast_url.strip()
        submission.screencast_file = None

    if file is not None:
        submission.screencast_file = await save_upload(file, f"{submission.id}/screencast", "screencast")
        submission.screencast_url = None

    await db.commit()
    return await get_submission(db, submission.id)


async def submit_for_check(db: AsyncSession, submission_id: UUID, user: User) -> Submission:
    submission = await get_submission(db, submission_id)
    await ensure_can_edit_submission(db, submission, user)

    artifact_checks: list[CheckType] = []
    if submission.repo_url or submission.repo_archive:
        artifact_checks.append(CheckType.code)
    if submission.doc_file:
        artifact_checks.append(CheckType.documentation)
    if submission.presentation:
        artifact_checks.append(CheckType.presentation)
    if submission.screencast_file or submission.screencast_url:
        artifact_checks.append(CheckType.screencast)

    if not artifact_checks:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No artifacts uploaded")

    existing = {check.check_type for check in submission.check_results}
    for check_type in artifact_checks:
        if check_type not in existing:
            db.add(CheckResult(submission_id=submission.id, check_type=check_type, status=CheckStatus.pending))

    submission.status = SubmissionStatus.checking
    submission.submitted_at = datetime.now(UTC)
    await db.commit()

    if CheckType.code in artifact_checks:
        analyze_code.delay(str(submission.id))
    if CheckType.documentation in artifact_checks:
        validate_documentation.delay(str(submission.id))
    if CheckType.presentation in artifact_checks:
        check_presentation.delay(str(submission.id))
    if CheckType.screencast in artifact_checks:
        process_video.delay(str(submission.id))

    return await get_submission(db, submission.id)
