from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.hackathon import Hackathon
from app.models.user import User
from app.schemas.hackathon import HackathonCreate, HackathonUpdate


async def create_hackathon(db: AsyncSession, payload: HackathonCreate, creator: User) -> Hackathon:
    hackathon = Hackathon(created_by=creator.id, **payload.model_dump())
    db.add(hackathon)
    await db.commit()
    await db.refresh(hackathon)
    return hackathon


async def list_hackathons(db: AsyncSession) -> list[Hackathon]:
    result = await db.execute(select(Hackathon).order_by(Hackathon.created_at.desc()))
    return list(result.scalars().all())


async def get_hackathon(db: AsyncSession, hackathon_id: UUID, with_related: bool = False) -> Hackathon:
    query = select(Hackathon).where(Hackathon.id == hackathon_id)
    if with_related:
        query = query.options(selectinload(Hackathon.teams), selectinload(Hackathon.criteria))

    result = await db.execute(query)
    hackathon = result.scalar_one_or_none()
    if hackathon is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
    return hackathon


def ensure_hackathon_creator(hackathon: Hackathon, user: User) -> None:
    if hackathon.created_by != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only creator can modify hackathon")


async def update_hackathon(
    db: AsyncSession,
    hackathon_id: UUID,
    payload: HackathonUpdate,
    user: User,
) -> Hackathon:
    hackathon = await get_hackathon(db, hackathon_id)
    ensure_hackathon_creator(hackathon, user)

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(hackathon, field, value)

    await db.commit()
    await db.refresh(hackathon)
    return hackathon
