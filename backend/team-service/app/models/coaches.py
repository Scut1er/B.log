from datetime import date
from typing import Optional

from app.db import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Coach(Base):
    __tablename__ = "coaches"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    birth_date: Mapped[Optional[date]] = mapped_column(nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(nullable=True, unique=True)

    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)

    # 💡 Обратная связь к команде
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="coach")
