from sqlalchemy import select, true
from sqlalchemy.ext.asyncio import AsyncSession

from src.team.schema import TeamMember
from src.users.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert_user(
        self, user_id: str, username: str, team_name: str, is_active: bool
    ) -> User:
        user = await self.get_user(user_id)
        if user:
            user.username = username
            user.team_name = team_name
            user.is_active = is_active
            return user
        user = User(
            user_id=user_id,
            username=username,
            team_name=team_name,
            is_active=is_active,
        )
        self.session.add(user)
        return user

    async def get_user(self, user_id: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def set_active(self, user_id: str, is_active: bool) -> User | None:
        user = await self.get_user(user_id)
        if not user:
            return None
        user.is_active = is_active
        return user

    async def get_active_candidates(
        self, team_name: str, exclude_ids: list[str]
    ) -> list[User]:
        result = await self.session.execute(
            select(User).where(
                User.team_name == team_name,
                User.is_active == true(),
                User.user_id.notin_(exclude_ids),
            )
        )
        return list(result.scalars().all())

    async def get_team_members(self, team_name: str) -> list[TeamMember]:
        result = await self.session.execute(
            select(User).where(User.team_name == team_name)
        )
        users = result.scalars().all()
        return [
            TeamMember(
                user_id=user.user_id,
                username=user.username,
                is_active=user.is_active,
            )
            for user in users
        ]
