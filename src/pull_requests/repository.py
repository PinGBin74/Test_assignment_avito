from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.pull_requests.models import (
    PullRequest,
    PullRequestStatus,
    ReviewerAssignment,
)
from src.utils import utc_now_naive


class PullRequestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, pr_id: str, name: str, author_id: str
    ) -> PullRequest:
        pr = PullRequest(
            pull_request_id=pr_id,
            pull_request_name=name,
            author_id=author_id,
            status=PullRequestStatus.OPEN,
            created_at=utc_now_naive(),
        )
        self.session.add(pr)
        return pr

    async def get(self, pr_id: str) -> PullRequest | None:
        result = await self.session.execute(
            select(PullRequest).where(PullRequest.pull_request_id == pr_id)
        )
        return result.scalar_one_or_none()

    async def merge(self, pr_id: str) -> PullRequest | None:
        result = await self.session.execute(
            update(PullRequest)
            .where(PullRequest.pull_request_id == pr_id)
            .values(status=PullRequestStatus.MERGED, merged_at=utc_now_naive())
            .returning(PullRequest)
        )
        return result.scalar_one_or_none()

    async def assign_reviewer(self, pr_id: str, user_id: str) -> None:
        self.session.add(
            ReviewerAssignment(pull_request_id=pr_id, user_id=user_id)
        )

    async def get_assigned_reviewers(self, pr_id: str) -> list[str]:
        result = await self.session.execute(
            select(ReviewerAssignment.user_id).where(
                ReviewerAssignment.pull_request_id == pr_id
            )
        )
        return result.scalars().all()

    async def replace_reviewer(
        self, pr_id: str, old_user_id: str, new_user_id: str
    ) -> None:
        await self.session.execute(
            delete(ReviewerAssignment).where(
                ReviewerAssignment.pull_request_id == pr_id,
                ReviewerAssignment.user_id == old_user_id,
            )
        )
        self.session.add(
            ReviewerAssignment(pull_request_id=pr_id, user_id=new_user_id)
        )

    async def get_reviewing_prs(self, user_id: str) -> list[PullRequest]:
        result = await self.session.execute(
            select(PullRequest)
            .join(ReviewerAssignment)
            .where(ReviewerAssignment.user_id == user_id)
        )
        return list(result.scalars().all())

    async def remove_reviewer(self, pr_id: str, user_id: str) -> None:
        await self.session.execute(
            delete(ReviewerAssignment).where(
                ReviewerAssignment.pull_request_id == pr_id,
                ReviewerAssignment.user_id == user_id,
            )
        )

    async def get_open_prs_by_reviewers(
        self, user_ids: list[str]
    ) -> list[PullRequest]:
        result = await self.session.execute(
            select(PullRequest)
            .join(ReviewerAssignment)
            .where(
                PullRequest.status == PullRequestStatus.OPEN,
                ReviewerAssignment.user_id.in_(user_ids),
            )
            .distinct()
        )
        return list(result.scalars().all())
