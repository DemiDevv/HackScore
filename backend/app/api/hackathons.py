from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import UserRole
from app.models.user import User
from app.schemas.hackathon import (
    HackathonCreate,
    HackathonDetailResponse,
    HackathonResponse,
    HackathonStatusUpdate,
    HackathonUpdate,
)
from app.services import hackathon_service
from app.utils.deps import get_current_user, get_db, require_role


router = APIRouter(prefix="/hackathons", tags=["hackathons"])


@router.post("/", response_model=HackathonResponse)
async def create_hackathon(
    payload: HackathonCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.organizer))],
) -> HackathonResponse:
    return await hackathon_service.create_hackathon(db, payload, current_user)


@router.get("/", response_model=list[HackathonResponse])
async def list_hackathons(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[HackathonResponse]:
    return await hackathon_service.list_hackathons(db)


@router.get("/{hackathon_id}", response_model=HackathonDetailResponse)
async def get_hackathon(
    hackathon_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> HackathonDetailResponse:
    hackathon = await hackathon_service.get_hackathon(db, hackathon_id, with_related=True)
    return HackathonDetailResponse(
        **HackathonResponse.model_validate(hackathon).model_dump(),
        teams_count=len(hackathon.teams),
        criteria_count=len(hackathon.criteria),
    )


@router.put("/{hackathon_id}", response_model=HackathonResponse)
async def update_hackathon(
    hackathon_id: UUID,
    payload: HackathonUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.organizer))],
) -> HackathonResponse:
    return await hackathon_service.update_hackathon(db, hackathon_id, payload, current_user)


@router.put("/{hackathon_id}/status", response_model=HackathonResponse)
async def update_hackathon_status(
    hackathon_id: UUID,
    payload: HackathonStatusUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.organizer))],
) -> HackathonResponse:
    return await hackathon_service.update_hackathon(
        db,
        hackathon_id,
        HackathonUpdate(status=payload.status),
        current_user,
    )
