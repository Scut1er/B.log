from datetime import datetime
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
    verification_token: Mapped[Optional[str]]
    verification_token_expires_at: Mapped[datetime] = mapped_column(TIMESTAMP)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))

    # role: Mapped["Roles"] = relationship(back_populates="users")
