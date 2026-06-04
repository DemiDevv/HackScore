from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.algo_task import AlgoSubmission, AlgoTask, AlgoTest
from app.models.enums import AlgoVerdict
from app.models.team import Team, TeamMember
from app.models.user import User
from app.schemas.algo import AlgoSubmitRequest, AlgoTaskCreate, AlgoTestCreate
from app.services.hackathon_service import ensure_hackathon_creator, get_hackathon
from app.workers.sandbox_runner import run_algo_solution


async def create_task(db: AsyncSession, payload: AlgoTaskCreate, organizer: User) -> AlgoTask:
    hackathon = await get_hackathon(db, payload.hackathon_id)
    ensure_hackathon_creator(hackathon, organizer)

    task = AlgoTask(
        hackathon_id=payload.hackathon_id,
        title=payload.title.strip(),
        description=payload.description,
        time_limit_ms=payload.time_limit_ms,
        memory_limit_mb=payload.memory_limit_mb,
        created_by=organizer.id,
    )
    db.add(task)
    await db.commit()
    return await get_task(db, task.id)


async def get_task(db: AsyncSession, task_id: UUID) -> AlgoTask:
    query = select(AlgoTask).where(AlgoTask.id == task_id).options(selectinload(AlgoTask.tests))
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Algorithm task not found")
    return task


async def list_tasks(db: AsyncSession, hackathon_id: UUID) -> list[AlgoTask]:
    await get_hackathon(db, hackathon_id)
    result = await db.execute(
        select(AlgoTask)
        .where(AlgoTask.hackathon_id == hackathon_id)
        .options(selectinload(AlgoTask.tests))
        .order_by(AlgoTask.title.asc())
    )
    return list(result.scalars().all())


async def add_tests(db: AsyncSession, task_id: UUID, payload: list[AlgoTestCreate], organizer: User) -> AlgoTask:
    task = await get_task(db, task_id)
    hackathon = await get_hackathon(db, task.hackathon_id)
    ensure_hackathon_creator(hackathon, organizer)

    for index, item in enumerate(payload):
        db.add(
            AlgoTest(
                task_id=task_id,
                input_data=item.input_data,
                expected_output=item.expected_output,
                is_sample=item.is_sample,
                order_index=item.order_index if item.order_index is not None else index,
            )
        )
    await db.commit()
    return await get_task(db, task_id)


async def get_user_team_for_hackathon(db: AsyncSession, hackathon_id: UUID, user: User) -> Team:
    result = await db.execute(
        select(Team)
        .join(TeamMember, TeamMember.team_id == Team.id)
        .where(Team.hackathon_id == hackathon_id, TeamMember.user_id == user.id)
    )
    team = result.scalar_one_or_none()
    if team is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not in a team for this hackathon")
    return team


async def submit_solution(db: AsyncSession, task_id: UUID, payload: AlgoSubmitRequest, user: User) -> AlgoSubmission:
    task = await get_task(db, task_id)
    team = await get_user_team_for_hackathon(db, task.hackathon_id, user)
    total_tests = len([test for test in task.tests if not test.is_sample])
    if total_tests == 0:
        total_tests = len(task.tests)

    submission = AlgoSubmission(
        task_id=task_id,
        user_id=user.id,
        team_id=team.id,
        language=payload.language,
        source_code=payload.source_code,
        verdict=AlgoVerdict.pending,
        test_total=total_tests,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    run_algo_solution.delay(str(submission.id))
    return submission


async def list_my_submissions(db: AsyncSession, task_id: UUID, user: User) -> list[AlgoSubmission]:
    result = await db.execute(
        select(AlgoSubmission)
        .where(AlgoSubmission.task_id == task_id, AlgoSubmission.user_id == user.id)
        .order_by(AlgoSubmission.submitted_at.desc())
    )
    return list(result.scalars().all())


async def get_submission(db: AsyncSession, submission_id: UUID, user: User | None = None) -> AlgoSubmission:
    submission = await db.get(AlgoSubmission, submission_id)
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Algorithm submission not found")
    if user is not None and submission.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view another user's submission")
    return submission
