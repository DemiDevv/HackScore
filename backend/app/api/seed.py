from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.seed import seed_database
from app.utils.deps import get_db


router = APIRouter(prefix="/seed", tags=["seed"])


@router.post("/")
async def seed(db: Annotated[AsyncSession, Depends(get_db)]) -> dict[str, int | str]:
    if settings.environment.lower() == "production":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Seed endpoint is disabled in production")
    return await seed_database(db)
