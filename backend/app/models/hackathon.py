import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import HackathonStatus


class Hackathon(Base):
    __tablename__ = "hackathons"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[HackathonStatus] = mapped_column(
        Enum(HackathonStatus, name="hackathon_status"),
        default=HackathonStatus.draft,
        nullable=False,
    )
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    creator = relationship("User", back_populates="hackathons")
    teams = relationship("Team", back_populates="hackathon", cascade="all, delete-orphan")
    criteria = relationship("Criterion", back_populates="hackathon", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="hackathon", cascade="all, delete-orphan")
    algo_tasks = relationship("AlgoTask", back_populates="hackathon", cascade="all, delete-orphan")
