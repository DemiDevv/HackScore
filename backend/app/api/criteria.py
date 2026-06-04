from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import UserRole
from app.models.user import User
from app.schemas.criterion import (
    CriteriaWeightsUpdate,
    CriterionCreate,
    CriterionResponse,
    CriterionUpdate,
)
from app.services import criterion_service
from app.utils.deps import get_current_user, get_db, require_role


router = APIRouter(prefix="/hackathons/{hackathon_id}/criteria", tags=["criteria"])


@router.post("/", response_model=CriterionResponse)
async def create_criterion(
    hackathon_id: UUID,
    payload: CriterionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.organizer))],
) -> CriterionResponse:
    return await criterion_service.create_criterion(db, hackathon_id, payload, current_user)


@router.get("/", response_model=list[CriterionResponse])
async def list_criteria(
    hackathon_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[CriterionResponse]:
    return await criterion_service.list_criteria(db, hackathon_id)


@router.put("/weights", response_model=list[CriterionResponse])
async def update_criteria_weights(
    hackathon_id: UUID,
    payload: CriteriaWeightsUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.organizer))],
) -> list[CriterionResponse]:
    return await criterion_service.update_weights(db, hackathon_id, payload, current_user)


@router.put("/{criterion_id}", response_model=CriterionResponse)
async def update_criterion(
    hackathon_id: UUID,
    criterion_id: UUID,
    payload: CriterionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.organizer))],
) -> CriterionResponse:
    return await criterion_service.update_criterion(db, hackathon_id, criterion_id, payload, current_user)


@router.delete("/{criterion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_criterion(
    hackathon_id: UUID,
    criterion_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.organizer))],
) -> None:
    await criterion_service.delete_criterion(db, hackathon_id, criterion_id, current_user)
