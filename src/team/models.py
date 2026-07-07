from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.models import Base


class Team(Base):
    __tablename__ = "teams"
    name: Mapped[str] = mapped_column(primary_key=True)
