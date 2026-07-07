import enum
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.models import Base
from src.utils import utc_now_naive


class PullRequestStatus(str, enum.Enum):
    OPEN = "OPEN"
    MERGED = "MERGED"


class PullRequest(Base):
    __tablename__ = "pull_requests"
    pull_request_id: Mapped[str] = mapped_column(primary_key=True)
    pull_request_name: Mapped[str] = mapped_column()
    author_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    status: Mapped[PullRequestStatus] = mapped_column(
        default=PullRequestStatus.OPEN
    )
    created_at: Mapped[datetime] = mapped_column(default=utc_now_naive)
    merged_at: Mapped[datetime] = mapped_column(nullable=True)


class ReviewerAssignment(Base):
    __tablename__ = "reviewer_assignments"
    pull_request_id: Mapped[str] = mapped_column(
        ForeignKey("pull_requests.pull_request_id"), primary_key=True
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id"), primary_key=True
    )
