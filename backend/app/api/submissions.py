from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.submission import SubmissionCreate, SubmissionResponse
from app.services import submission_service
from app.utils.deps import get_current_user, get_db


router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("/", response_model=SubmissionResponse)
async def create_submission(
    payload: SubmissionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SubmissionResponse:
    return await submission_service.create_submission(db, payload, current_user)


@router.get("/team/{team_id}", response_model=SubmissionResponse)
async def get_team_submission(
    team_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SubmissionResponse:
    return await submission_service.get_submission_by_team(db, team_id, current_user)


@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SubmissionResponse:
    return await submission_service.get_submission_for_user(db, submission_id, current_user)


@router.put("/{submission_id}/repo", response_model=SubmissionResponse)
async def update_repo(
    submission_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    repo_url: Annotated[str | None, Form()] = None,
    repo_archive: Annotated[UploadFile | None, File()] = None,
) -> SubmissionResponse:
    return await submission_service.update_repo(db, submission_id, current_user, repo_url, repo_archive)


@router.put("/{submission_id}/documentation", response_model=SubmissionResponse)
async def update_documentation(
    submission_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    file: Annotated[UploadFile, File()],
) -> SubmissionResponse:
    return await submission_service.update_documentation(db, submission_id, current_user, file)


@router.put("/{submission_id}/presentation", response_model=SubmissionResponse)
async def update_presentation(
    submission_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    file: Annotated[UploadFile, File()],
) -> SubmissionResponse:
    return await submission_service.update_presentation(db, submission_id, current_user, file)


@router.put("/{submission_id}/screencast", response_model=SubmissionResponse)
async def update_screencast(
    submission_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    screencast_url: Annotated[str | None, Form()] = None,
    file: Annotated[UploadFile | None, File()] = None,
) -> SubmissionResponse:
    return await submission_service.update_screencast(db, submission_id, current_user, screencast_url, file)


@router.post("/{submission_id}/submit", response_model=SubmissionResponse)
async def submit_for_check(
    submission_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SubmissionResponse:
    return await submission_service.submit_for_check(db, submission_id, current_user)
