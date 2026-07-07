from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.models import Base


class User(Base):
    __tablename__ = "users"
    user_id: Mapped[str] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()
    team_name: Mapped[str] = mapped_column(ForeignKey("teams.name"))
    is_active: Mapped[bool] = mapped_column(default=True)
