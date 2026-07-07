from pydantic import BaseModel

from src.pull_requests.schema import PullRequestShort

class SetIsActiveRequest(BaseModel):
    user_id: str
    is_active: bool

class UserOut(BaseModel):
    user_id: str
    username: str
    team_name: str
    is_active: bool


class GetReviewResponse(BaseModel):
    user_id: str
    pull_requests: list[PullRequestShort]
