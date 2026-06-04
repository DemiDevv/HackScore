from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import UserRole
from app.models.team import Team, TeamMember
from app.models.user import User
from app.schemas.team import TeamCreate, TeamMemberResponse, TeamResponse
from app.services.hackathon_service import get_hackathon


def serialize_team(team: Team) -> TeamResponse:
    members = [
        TeamMemberResponse(
            id=member.id,
            user_id=member.user_id,
            email=member.user.email,
            full_name=member.user.full_name,
            role=member.user.role,
            is_captain=member.is_captain,
        )
        for member in team.members
    ]
    return TeamResponse(
        id=team.id,
        name=team.name,
        hackathon_id=team.hackathon_id,
        created_at=team.created_at,
        members=members,
    )


async def get_team(db: AsyncSession, team_id: UUID) -> Team:
    result = await db.execute(
        select(Team)
        .where(Team.id == team_id)
        .options(selectinload(Team.members).selectinload(TeamMember.user))
    )
    team = result.scalar_one_or_none()
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return team


def ensure_team_in_hackathon(team: Team, hackathon_id: UUID) -> None:
    if team.hackathon_id != hackathon_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found in hackathon")


async def list_teams(db: AsyncSession, hackathon_id: UUID) -> list[TeamResponse]:
    await get_hackathon(db, hackathon_id)
    result = await db.execute(
        select(Team)
        .where(Team.hackathon_id == hackathon_id)
        .options(selectinload(Team.members).selectinload(TeamMember.user))
        .order_by(Team.created_at.desc())
    )
    return [serialize_team(team) for team in result.scalars().all()]


async def create_team(db: AsyncSession, hackathon_id: UUID, payload: TeamCreate, user: User) -> TeamResponse:
    await get_hackathon(db, hackathon_id)

    team = Team(name=payload.name.strip(), hackathon_id=hackathon_id)
    db.add(team)
    await db.flush()

    db.add(TeamMember(team_id=team.id, user_id=user.id, is_captain=True))
    await db.commit()

    return serialize_team(await get_team(db, team.id))


async def ensure_team_captain(db: AsyncSession, team_id: UUID, user: User) -> None:
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user.id,
            TeamMember.is_captain.is_(True),
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only captain can manage team members")


async def add_member(
    db: AsyncSession,
    hackathon_id: UUID,
    team_id: UUID,
    email: str,
    current_user: User,
) -> TeamResponse:
    team = await get_team(db, team_id)
    ensure_team_in_hackathon(team, hackathon_id)
    await ensure_team_captain(db, team_id, current_user)

    result = await db.execute(select(User).where(User.email == email.strip().lower()))
    user = result.scalar_one_or_none()
    if user is None or user.role != UserRole.participant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")

    existing = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == user.id)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already in team")

    db.add(TeamMember(team_id=team_id, user_id=user.id, is_captain=False))
    await db.commit()
    return serialize_team(await get_team(db, team.id))


async def remove_member(
    db: AsyncSession,
    hackathon_id: UUID,
    team_id: UUID,
    user_id: UUID,
    current_user: User,
) -> TeamResponse:
    team = await get_team(db, team_id)
    ensure_team_in_hackathon(team, hackathon_id)
    await ensure_team_captain(db, team_id, current_user)

    result = await db.execute(select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == user_id))
    member = result.scalar_one_or_none()
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team member not found")
    if member.is_captain:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Captain cannot be removed")

    await db.delete(member)
    await db.commit()
    return serialize_team(await get_team(db, team.id))
