import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import CheckStatus, CheckType


class CheckResult(Base):
    __tablename__ = "check_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("submissions.id", ondelete="CASCADE"),
        nullable=False,
    )
    check_type: Mapped[CheckType] = mapped_column(Enum(CheckType, name="check_type"), nullable=False)
    status: Mapped[CheckStatus] = mapped_column(
        Enum(CheckStatus, name="check_status"),
        default=CheckStatus.pending,
        nullable=False,
    )
    score: Mapped[float | None] = mapped_column(Float)
    report: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    submission = relationship("Submission", back_populates="check_results")
