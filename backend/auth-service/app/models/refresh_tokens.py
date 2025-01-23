from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.db.db import Base
from app.schemas import RefreshTokenSchema


class RefreshTokens(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    token: Mapped[str] = mapped_column(nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime] = mapped_column(nullable=False)

    # user: Mapped["Users"] = relationship(back_populates="refresh_tokens")

    def to_read_model(self) -> RefreshTokenSchema:
        return RefreshTokenSchema(
            user_id=self.user_id,
            token=self.token,
            created_at=self.created_at,
            expires_at=self.expires_at
        )
