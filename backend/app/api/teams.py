from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import UserRole
from app.models.user import User
from app.schemas.team import TeamCreate, TeamMemberAdd, TeamResponse
from app.services import team_service
from app.utils.deps import get_current_user, get_db, require_role


router = APIRouter(prefix="/hackathons/{hackathon_id}/teams", tags=["teams"])


@router.post("/", response_model=TeamResponse)
async def create_team(
    hackathon_id: UUID,
    payload: TeamCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.participant))],
) -> TeamResponse:
    return await team_service.create_team(db, hackathon_id, payload, current_user)


@router.get("/", response_model=list[TeamResponse])
async def list_teams(
    hackathon_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[TeamResponse]:
    return await team_service.list_teams(db, hackathon_id)


@router.post("/{team_id}/members", response_model=TeamResponse)
async def add_team_member(
    hackathon_id: UUID,
    team_id: UUID,
    payload: TeamMemberAdd,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.participant))],
) -> TeamResponse:
    return await team_service.add_member(db, hackathon_id, team_id, payload.email, current_user)


@router.delete("/{team_id}/members/{user_id}", response_model=TeamResponse)
async def remove_team_member(
    hackathon_id: UUID,
    team_id: UUID,
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.participant))],
) -> TeamResponse:
    return await team_service.remove_member(db, hackathon_id, team_id, user_id, current_user)
