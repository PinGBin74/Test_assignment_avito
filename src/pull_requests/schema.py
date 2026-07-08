from datetime import datetime

from pydantic import BaseModel, Field

from pull_requests.models import PullRequestStatus


class PullRequestOut(BaseModel):
    model_config = {"populate_by_name": True}

    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PullRequestStatus
    assigned_reviewers: list[str]
    created_at: datetime | None = Field(default=None, alias="createdAt")
    merged_at: datetime | None = Field(default=None, alias="mergedAt")


class PullRequestShort(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PullRequestStatus


class CreatePRRequest(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str


class MergePRRequest(BaseModel):
    pull_request_id: str


class ReassignRequest(BaseModel):
    pull_request_id: str
    old_user_id: str


class ReassignResponse(BaseModel):
    pr: PullRequestOut
    replaced_by: str
