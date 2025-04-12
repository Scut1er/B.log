from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date
from typing import Optional
import enum

from app.db import Base


class PlayerPosition(enum.Enum):
    POINT_GUARD = "PG"
    SHOOTING_GUARD = "SG"
    SMALL_FORWARD = "SF"
    POWER_FORWARD = "PF"
    CENTER = "C"


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    birth_date: Mapped[Optional[date]] = mapped_column(nullable=True)
    height_cm: Mapped[Optional[int]] = mapped_column(nullable=True)
    weight_kg: Mapped[Optional[int]] = mapped_column(nullable=True)

    position: Mapped[Optional[PlayerPosition]] = mapped_column(Enum(PlayerPosition), nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(nullable=True, unique=True)

    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)

    # 💡 Обратная связь к команде
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="players")
