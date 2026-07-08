from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database import get_db_session
from stats.repository import StatsService

router = APIRouter(tags=["Stats"])


@router.get("/stats")
async def get_stats(
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    service = StatsService(session)
    return await service.get_stats()
