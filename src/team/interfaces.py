from typing import Protocol

from src.team.models import Team


class TeamRepositoryProtocol(Protocol):
    async def create_team(self, name: str) -> Team: ...

    async def get_team(self, name: str) -> Team | None: ...
