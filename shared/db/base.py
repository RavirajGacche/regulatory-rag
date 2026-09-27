from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """All models inherit from this. It holds the shared metadata registry"""

    def __repr__(self) -> str:
        pk: Any = getattr(self, "id", None)
        return f"<{type(self).__name__} id={pk}>"


class CreatedAtMixin:
    """For insert only table"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class TimeStampMixin(CreatedAtMixin):
    """Audit columns for every table."""

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
