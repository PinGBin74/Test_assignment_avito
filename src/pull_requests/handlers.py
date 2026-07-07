from fastapi import APIRouter, Depends

from src.dependencies import get_pr_service
from src.pull_requests.schema import (
    CreatePRRequest,
    MergePRRequest,
    PullRequestOut,
    ReassignRequest,
    ReassignResponse,
)
from src.pull_requests.service import PullRequestService

router = APIRouter(tags=["PullRequests"])


@router.post("/pullRequest/create", status_code=201)
async def create_pr(
    body: CreatePRRequest,
    service: PullRequestService = Depends(get_pr_service),
) -> PullRequestOut:
    pr = await service.create_pr(body)
    return pr


@router.post("/pullRequest/merge")
async def merge_pr(
    body: MergePRRequest,
    service: PullRequestService = Depends(get_pr_service),
) -> PullRequestOut:
    pr = await service.merge_pr(body.pull_request_id)
    return pr


@router.post("/pullRequest/reassign")
async def reassign(
    body: ReassignRequest,
    service: PullRequestService = Depends(get_pr_service),
) -> ReassignResponse:
    result = await service.reassign(body.pull_request_id, body.old_user_id)
    return result
