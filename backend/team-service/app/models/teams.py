from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

from app.db import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    city: Mapped[str] = mapped_column(nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(nullable=True, unique=True)

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # 💡 Отношение к игрокам (один ко многим)
    players: Mapped[List["Player"]] = relationship("Player", back_populates="team", cascade="all, delete",
                                                   passive_deletes=True)

    # 💡 Отношение к тренеру (один к одному)
    coach: Mapped[Optional["Coach"]] = relationship("Coach", back_populates="team", uselist=False,
                                                    cascade="all, delete", passive_deletes=True)
