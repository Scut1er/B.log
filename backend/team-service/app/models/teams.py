from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from app.db import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
