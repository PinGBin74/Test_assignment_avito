from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import NotFoundError, TeamExistsError
from src.team.interfaces import TeamRepositoryProtocol
from src.team.schema import Team, TeamMember
from src.users.interfaces import UserRepositoryProtocol


class TeamService:
    def __init__(
        self,
        team_repo: TeamRepositoryProtocol | None = None,
        user_repo: UserRepositoryProtocol | None = None,
        session: AsyncSession | None = None,
    ):
        self.team_repo = team_repo
        self.user_repo = user_repo
        self.session = session

    async def add_team(
        self, team_name: str, members: list[TeamMember]
    ) -> Team:
        existing = await self.team_repo.get_team(team_name)
        if existing:
            raise TeamExistsError(team_name)

        await self.team_repo.create_team(team_name)
        for member in members:
            await self.user_repo.upsert_user(
                member.user_id, member.username, team_name, member.is_active
            )

        await self.session.commit()
        return await self.get_team(team_name)

    async def get_team(self, team_name: str) -> Team:
        team = await self.team_repo.get_team(team_name)
        if not team:
            raise NotFoundError("team", team_name)

        members = await self.user_repo.get_team_members(team_name)
        return Team(team_name=team_name, members=members)
