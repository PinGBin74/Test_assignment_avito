import random

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import (
    NoCandidateError,
    NotAssignedError,
    NotFoundError,
    PRExistsError,
    PRMergedError,
)
from src.pull_requests.interfaces import PullRequestRepositoryProtocol
from src.pull_requests.schema import (
    CreatePRRequest,
    PullRequestOut,
    PullRequestShort,
    ReassignResponse,
)
from src.users.interfaces import UserRepositoryProtocol
from src.users.schema import GetReviewResponse


class PullRequestService:
    def __init__(
        self,
        pr_repo: PullRequestRepositoryProtocol | None = None,
        user_repo: UserRepositoryProtocol | None = None,
        session: AsyncSession | None = None,
    ):
        self.pr_repo = pr_repo
        self.user_repo = user_repo
        self.session = session

    async def create_pr(self, req: CreatePRRequest) -> PullRequestOut:
        existing = await self.pr_repo.get(req.pull_request_id)
        if existing:
            raise PRExistsError(req.pull_request_id)

        author = await self.user_repo.get_user(req.author_id)
        if not author:
            raise NotFoundError("user", req.author_id)

        candidates = await self.user_repo.get_active_candidates(
            author.team_name, exclude_ids=[req.author_id]
        )
        selected = random.sample(candidates, min(2, len(candidates)))

        pr = await self.pr_repo.create(
            req.pull_request_id, req.pull_request_name, req.author_id
        )
        assigned = []
        for reviewer in selected:
            assigned.append(reviewer.user_id)
            await self.pr_repo.assign_reviewer(
                req.pull_request_id, reviewer.user_id
            )

        await self.session.commit()
        return PullRequestOut(
            pull_request_id=pr.pull_request_id,
            pull_request_name=pr.pull_request_name,
            author_id=pr.author_id,
            status=pr.status.value,
            assigned_reviewers=assigned,
            created_at=pr.created_at,
        )

    async def merge_pr(self, pr_id: str) -> PullRequestOut:
        pr = await self.pr_repo.get(pr_id)
        if not pr:
            raise NotFoundError("PR", pr_id)

        if pr.status.value != "MERGED":
            pr = await self.pr_repo.merge(pr_id)
            await self.session.commit()

        reviewers = await self.pr_repo.get_assigned_reviewers(pr_id)
        return PullRequestOut(
            pull_request_id=pr.pull_request_id,
            pull_request_name=pr.pull_request_name,
            author_id=pr.author_id,
            status=pr.status.value,
            assigned_reviewers=reviewers,
            created_at=pr.created_at,
            merged_at=pr.merged_at,
        )

    async def reassign(self, pr_id: str, old_user_id: str) -> ReassignResponse:
        pr = await self.pr_repo.get(pr_id)
        if not pr:
            raise NotFoundError("PR", pr_id)
        if pr.status.value == "MERGED":
            raise PRMergedError(pr_id)

        reviewers = await self.pr_repo.get_assigned_reviewers(pr_id)
        if old_user_id not in reviewers:
            raise NotAssignedError(old_user_id, pr_id)

        old_user = await self.user_repo.get_user(old_user_id)
        if not old_user:
            raise NotFoundError("user", old_user_id)

        candidates = await self.user_repo.get_active_candidates(
            old_user.team_name,
            exclude_ids=reviewers + [pr.author_id],
        )
        if not candidates:
            raise NoCandidateError(old_user.team_name)

        new_user = random.choice(candidates)
        await self.pr_repo.replace_reviewer(
            pr_id, old_user_id, new_user.user_id
        )

        await self.session.commit()
        updated_reviewers = await self.pr_repo.get_assigned_reviewers(pr_id)
        return ReassignResponse(
            pr=PullRequestOut(
                pull_request_id=pr.pull_request_id,
                pull_request_name=pr.pull_request_name,
                author_id=pr.author_id,
                status=pr.status.value,
                assigned_reviewers=updated_reviewers,
                created_at=pr.created_at,
                merged_at=pr.merged_at,
            ),
            replaced_by=new_user.user_id,
        )

    async def get_reviewing_prs(self, user_id: str) -> GetReviewResponse:
        user = await self.user_repo.get_user(user_id)
        if not user:
            return GetReviewResponse(user_id=user_id, pull_requests=[])

        prs = await self.pr_repo.get_reviewing_prs(user_id)
        return GetReviewResponse(
            user_id=user_id,
            pull_requests=[
                PullRequestShort(
                    pull_request_id=p.pull_request_id,
                    pull_request_name=p.pull_request_name,
                    author_id=p.author_id,
                    status=p.status.value,
                )
                for p in prs
            ],
        )
