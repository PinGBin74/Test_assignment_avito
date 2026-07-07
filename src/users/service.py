from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import NotFoundError
from src.users.interfaces import UserRepositoryProtocol
from src.users.schema import UserOut


class UserService:
    def __init__(
        self,
        user_repo: UserRepositoryProtocol | None = None,
        session: AsyncSession | None = None,
    ):
        self.user_repo = user_repo
        self.session = session

    async def set_is_active(self, user_id: str, is_active: bool) -> UserOut:
        user = await self.user_repo.set_active(user_id, is_active)
        if not user:
            raise NotFoundError("user", user_id)
        await self.session.commit()
        return UserOut(
            user_id=user.user_id,
            username=user.username,
            team_name=user.team_name,
            is_active=user.is_active,
        )
