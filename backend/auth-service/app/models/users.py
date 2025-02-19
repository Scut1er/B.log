from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(nullable=True)  # пустое при OAuth
    salt: Mapped[Optional[str]] = mapped_column(nullable=True)  # пустое при OAuth
    fullname: Mapped[Optional[str]] = mapped_column(nullable=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), default=1, nullable=False)

    # role: Mapped["Role"] = relationship(back_populates="users")
    # oauth_accounts: Mapped["OAuthAccount"]  = relationship("OAuthAccount", back_populates="user", cascade="all, delete-orphan")
