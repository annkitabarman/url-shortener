from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class URL(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    short_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
    )

    original_url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
