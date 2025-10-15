from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Boolean
from db.base import Base, PkMixin, TimestampMixin


class User(Base, PkMixin, TimestampMixin):
    name: Mapped[str]
    last_name: Mapped[str]
    father_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    passwd: Mapped[str]
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")


    def __repr__(self) -> str:
        """Строковое представление объекта для удобства отладки."""
        return f"<{self.__class__.__name__}({self.id=}, {self.email=}, {self.is_active=})>"
