from fastapi import APIRouter, Depends

from src.dependencies import get_stats_service
from src.stats.repository import StatsRepository

router = APIRouter(tags=["Stats"])


@router.get("/stats")
async def get_stats(
    repository: StatsRepository = Depends(get_stats_service),
) -> dict:
    return await repository.get_stats()
