from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class PullRequestOut(BaseModel):
    model_config = {"populate_by_name": True}

    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: Literal["OPEN", "MERGED"]
    assigned_reviewers: list[str]
    created_at: datetime | None = Field(default=None, alias="createdAt")
    merged_at: datetime | None = Field(default=None, alias="mergedAt")


class PullRequestShort(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: Literal["OPEN", "MERGED"]


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
    pull_request: PullRequestOut
    replaced_by: str

