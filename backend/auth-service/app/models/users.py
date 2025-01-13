from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.db.db import Base


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[Optional[str]] = mapped_column(unique=True)
    password_hash: Mapped[str]
    fullname: Mapped[Optional[str]]
    is_verified: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))

    # role: Mapped["Roles"] = relationship(back_populates="users")
