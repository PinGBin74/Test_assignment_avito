from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.team.models import Team


class TeamRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_team(self, name: str) -> Team:
        team = Team(name=name)
        self.session.add(team)
        return team

    async def get_team(self, name: str) -> Team | None:
        result = await self.session.execute(
            select(Team).where(Team.name == name)
        )
        return result.scalar_one_or_none()
