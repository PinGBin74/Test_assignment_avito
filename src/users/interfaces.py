from typing import Protocol

from src.team.schema import TeamMember
from src.users.models import User


class UserRepositoryProtocol(Protocol):
    async def upsert_user(
        self, user_id: str, username: str, team_name: str, is_active: bool
    ) -> User: ...

    async def get_user(self, user_id: str) -> User | None: ...

    async def set_active(
        self, user_id: str, is_active: bool
    ) -> User | None: ...

    async def get_active_candidates(
        self, team_name: str, exclude_ids: list[str]
    ) -> list[User]: ...

    async def get_team_members(self, team_name: str) -> list[TeamMember]: ...
