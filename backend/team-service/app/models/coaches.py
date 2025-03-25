from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from app.db import Base


class Coach(Base):
    __tablename__ = "coaches"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    photo_url: Mapped[Optional[str]] = mapped_column(nullable=True)

    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
