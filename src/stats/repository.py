from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.pull_requests.models import (
    PullRequest,
    PullRequestStatus,
    ReviewerAssignment,
)


class StatsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_stats(self) -> dict:
        result = await self.session.execute(
            select(ReviewerAssignment.user_id, func.count("*")).group_by(
                ReviewerAssignment.user_id
            )
        )
        assignments_by_user = dict(result.all())

        total = await self.session.scalar(
            select(func.count("*")).select_from(PullRequest)
        )
        open_count = await self.session.scalar(
            select(func.count("*"))
            .select_from(PullRequest)
            .where(PullRequest.status == PullRequestStatus.OPEN)
        )
        merged = await self.session.scalar(
            select(func.count("*"))
            .select_from(PullRequest)
            .where(PullRequest.status == PullRequestStatus.MERGED)
        )

        return {
            "assignments_by_user": assignments_by_user,
            "total_prs": total or 0,
            "open_prs": open_count or 0,
            "merged_prs": merged or 0,
        }
