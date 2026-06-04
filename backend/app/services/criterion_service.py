from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.criterion import Criterion
from app.models.user import User
from app.schemas.criterion import CriteriaWeightsUpdate, CriterionCreate, CriterionUpdate
from app.services.hackathon_service import ensure_hackathon_creator, get_hackathon


async def get_criterion(db: AsyncSession, criterion_id: UUID) -> Criterion:
    result = await db.execute(select(Criterion).where(Criterion.id == criterion_id))
    criterion = result.scalar_one_or_none()
    if criterion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Criterion not found")
    return criterion


def ensure_criterion_in_hackathon(criterion: Criterion, hackathon_id: UUID) -> None:
    if criterion.hackathon_id != hackathon_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Criterion not found in hackathon")


async def list_criteria(db: AsyncSession, hackathon_id: UUID) -> list[Criterion]:
    await get_hackathon(db, hackathon_id)
    result = await db.execute(
        select(Criterion)
        .where(Criterion.hackathon_id == hackathon_id)
        .order_by(Criterion.order_index.asc().nullslast(), Criterion.name.asc())
    )
    return list(result.scalars().all())


async def create_criterion(
    db: AsyncSession,
    hackathon_id: UUID,
    payload: CriterionCreate,
    user: User,
) -> Criterion:
    hackathon = await get_hackathon(db, hackathon_id)
    ensure_hackathon_creator(hackathon, user)

    criterion = Criterion(hackathon_id=hackathon_id, **payload.model_dump())
    db.add(criterion)
    await db.commit()
    await db.refresh(criterion)
    return criterion


async def update_criterion(
    db: AsyncSession,
    hackathon_id: UUID,
    criterion_id: UUID,
    payload: CriterionUpdate,
    user: User,
) -> Criterion:
    criterion = await get_criterion(db, criterion_id)
    ensure_criterion_in_hackathon(criterion, hackathon_id)
    hackathon = await get_hackathon(db, criterion.hackathon_id)
    ensure_hackathon_creator(hackathon, user)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(criterion, field, value)

    await db.commit()
    await db.refresh(criterion)
    return criterion


async def delete_criterion(db: AsyncSession, hackathon_id: UUID, criterion_id: UUID, user: User) -> None:
    criterion = await get_criterion(db, criterion_id)
    ensure_criterion_in_hackathon(criterion, hackathon_id)
    hackathon = await get_hackathon(db, criterion.hackathon_id)
    ensure_hackathon_creator(hackathon, user)

    await db.delete(criterion)
    await db.commit()


async def update_weights(
    db: AsyncSession,
    hackathon_id: UUID,
    payload: CriteriaWeightsUpdate,
    user: User,
) -> list[Criterion]:
    hackathon = await get_hackathon(db, hackathon_id)
    ensure_hackathon_creator(hackathon, user)

    total = sum(item.weight for item in payload.weights)
    if abs(total - 1.0) > 0.0001:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Weights sum must equal 1.0")

    criteria = await list_criteria(db, hackathon_id)
    by_id = {criterion.id: criterion for criterion in criteria}

    missing = [item.id for item in payload.weights if item.id not in by_id]
    if missing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Criterion not found in hackathon")

    for item in payload.weights:
        by_id[item.id].weight = item.weight

    await db.commit()
    return await list_criteria(db, hackathon_id)
