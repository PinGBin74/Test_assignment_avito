from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database import get_db_session
from src.pull_requests.service import PullRequestService
from src.stats.repository import StatsRepository
from src.team.service import TeamService
from src.users.service import UserService


async def get_team_service(
    session: AsyncSession = Depends(get_db_session),
) -> TeamService:
    return TeamService(session=session)


async def get_user_service(
    session: AsyncSession = Depends(get_db_session),
) -> UserService:
    return UserService(session=session)


async def get_pr_service(
    session: AsyncSession = Depends(get_db_session),
) -> PullRequestService:
    return PullRequestService(session=session)


async def get_stats_service(
    session: AsyncSession = Depends(get_db_session),
) -> StatsRepository:
    return StatsRepository(session=session)
