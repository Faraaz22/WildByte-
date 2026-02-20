"""Schema model for database schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.database import Base

if TYPE_CHECKING:
    from src.models.database import Database
    from src.models.table import Table


class Schema(Base):
    """
    Database schema metadata.
    
    Represents a schema/namespace within a database (e.g., 'public', 'dbo').
    """

    __tablename__ = "schemas"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign keys
    database_id: Mapped[int] = mapped_column(
        ForeignKey("databases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Required fields
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Optional fields
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    database: Mapped["Database"] = relationship("Database", back_populates="schemas")
    tables: Mapped[list["Table"]] = relationship(
        "Table",
        back_populates="schema",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Schema(id={self.id}, name='{self.name}', database_id={self.database_id})>"
