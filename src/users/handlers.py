from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from src.dependencies import get_pr_service, get_user_service
from src.pull_requests.service import PullRequestService
from src.users.schema import GetReviewResponse, SetIsActiveRequest
from src.users.service import UserService

router = APIRouter(tags=["Users"])




@router.post("/users/setIsActive")
async def set_is_active(
    body: SetIsActiveRequest,
    service: UserService = Depends(get_user_service),
) -> SetIsActiveRequest:
    user = await service.set_is_active(body.user_id, body.is_active)
    return { user}


@router.get("/users/getReview")
async def get_review(
    user_id: str = Query(),
    service: PullRequestService = Depends(get_pr_service),
) -> GetReviewResponse:
    return await service.get_reviewing_prs(user_id)
