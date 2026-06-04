from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import UserRole
from app.models.user import User
from app.schemas.algo import (
    AlgoSubmissionResponse,
    AlgoSubmitRequest,
    AlgoTaskCreate,
    AlgoTaskResponse,
    AlgoTestCreate,
)
from app.services import algo_service
from app.utils.deps import get_current_user, get_db, require_role


router = APIRouter(prefix="/algo", tags=["algo"])


@router.post("/tasks", response_model=AlgoTaskResponse)
async def create_task(
    payload: AlgoTaskCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.organizer))],
) -> AlgoTaskResponse:
    return await algo_service.create_task(db, payload, current_user)


@router.post("/tasks/{task_id}/tests", response_model=AlgoTaskResponse)
async def add_tests(
    task_id: UUID,
    payload: list[AlgoTestCreate],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.organizer))],
) -> AlgoTaskResponse:
    return await algo_service.add_tests(db, task_id, payload, current_user)


@router.get("/tasks", response_model=list[AlgoTaskResponse])
async def list_tasks(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    hackathon_id: UUID = Query(...),
) -> list[AlgoTaskResponse]:
    return await algo_service.list_tasks(db, hackathon_id)


@router.get("/tasks/{task_id}", response_model=AlgoTaskResponse)
async def get_task(
    task_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> AlgoTaskResponse:
    return await algo_service.get_task(db, task_id)


@router.post("/tasks/{task_id}/submit", response_model=AlgoSubmissionResponse)
async def submit_solution(
    task_id: UUID,
    payload: AlgoSubmitRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.participant))],
) -> AlgoSubmissionResponse:
    return await algo_service.submit_solution(db, task_id, payload, current_user)


@router.get("/tasks/{task_id}/submissions", response_model=list[AlgoSubmissionResponse])
async def list_my_submissions(
    task_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.participant))],
) -> list[AlgoSubmissionResponse]:
    return await algo_service.list_my_submissions(db, task_id, current_user)


@router.get("/submissions/{submission_id}", response_model=AlgoSubmissionResponse)
async def get_submission(
    submission_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.participant))],
) -> AlgoSubmissionResponse:
    return await algo_service.get_submission(db, submission_id, current_user)
