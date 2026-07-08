import random

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import NotFoundError, TeamExistsError
from src.pull_requests.interfaces import PullRequestRepositoryProtocol
from src.pull_requests.repository import PullRequestRepository
from src.team.interfaces import TeamRepositoryProtocol
from src.team.repository import TeamRepository
from src.team.schema import Team, TeamMember
from src.users.interfaces import UserRepositoryProtocol
from src.users.repository import UserRepository


class TeamService:
    def __init__(
        self,
        team_repo: TeamRepositoryProtocol | None = None,
        user_repo: UserRepositoryProtocol | None = None,
        pr_repo: PullRequestRepositoryProtocol | None = None,
        session: AsyncSession | None = None,
    ):
        self.team_repo = team_repo or TeamRepository(session)
        self.user_repo = user_repo or UserRepository(session)
        self.pr_repo = pr_repo or PullRequestRepository(session)
        self.session = session

    async def add_team(
        self, team_name: str, members: list[TeamMember]
    ) -> Team:
        existing = await self.team_repo.get_team(team_name)
        if existing:
            raise TeamExistsError(team_name)
        try:
            await self.team_repo.create_team(team_name)
            for member in members:
                await self.user_repo.upsert_user(
                    member.user_id,
                    member.username,
                    team_name,
                    member.is_active,
                )
            await self.session.commit()
        except IntegrityError:
            raise TeamExistsError(team_name) from None

        return await self.get_team(team_name)

    async def deactivate_team(self, team_name: str) -> dict:
        existing = await self.team_repo.get_team(team_name)
        if not existing:
            raise NotFoundError("team", team_name)

        members = await self.user_repo.get_team_members(team_name)
        user_ids = [m.user_id for m in members]

        await self.user_repo.user_set_inactive(team_name)

        affected_prs = await self.pr_repo.get_open_prs_by_reviewers(user_ids)

        replaced = 0
        for pr in affected_prs:
            reviewers = await self.pr_repo.get_assigned_reviewers(
                pr.pull_request_id
            )
            author = await self.user_repo.get_user(pr.author_id)
            if not author:
                continue

            for old_user_id in list(reviewers):
                if old_user_id not in user_ids:
                    continue

                exclude = [r for r in reviewers if r != old_user_id] + [
                    pr.author_id
                ]
                candidates = await self.user_repo.get_active_candidates(
                    author.team_name, exclude_ids=exclude
                )
                if candidates:
                    new_user = random.choice(candidates)
                    await self.pr_repo.replace_reviewer(
                        pr.pull_request_id, old_user_id, new_user.user_id
                    )
                    reviewers = [
                        new_user.user_id if r == old_user_id else r
                        for r in reviewers
                    ]
                    replaced += 1
                else:
                    await self.pr_repo.remove_reviewer(
                        pr.pull_request_id, old_user_id
                    )
                    reviewers.remove(old_user_id)

        await self.session.commit()
        return {
            "team_name": team_name,
            "deactivated": len(user_ids),
            "reassigned_reviewers": replaced,
        }

    async def get_team(self, team_name: str) -> Team:
        team = await self.team_repo.get_team(team_name)
        if not team:
            raise NotFoundError("team", team_name)

        members = await self.user_repo.get_team_members(team_name)
        return Team(team_name=team_name, members=members)
