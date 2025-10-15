from datetime import datetime
from typing import Dict, Any

from sqlalchemy import Integer, DateTime, text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from db.session import engine
from sqlalchemy.ext.asyncio import AsyncAttrs


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("timezone('utc', now())"),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.timezone('utc', func.now()),
        nullable=False,
    )


class PkMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'

    def to_dict(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        """Строковое представление объекта для удобства отладки."""
        return f"<{self.__class__.__name__}(id={self.id}, created_at={self.created_at}, updated_at={self.updated_at})>"
