import datetime
import uuid

from sqlalchemy import UUID, Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.jwt_auth.database.core import Base


class CreatedAtMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=datetime.datetime.now,
    )


class UpdatedAtMixin:
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class TimestampsMixin(CreatedAtMixin, UpdatedAtMixin):
    pass


class IDMixin:
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class User(IDMixin, TimestampsMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text, unique=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
