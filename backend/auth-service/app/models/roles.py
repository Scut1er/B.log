from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from app.db.db import Base


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    role_name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[Optional[str]]

