import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import SubmissionStatus


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
    )
    hackathon_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hackathons.id", ondelete="CASCADE"),
        nullable=False,
    )
    repo_url: Mapped[str | None] = mapped_column(String(1024))
    repo_archive: Mapped[str | None] = mapped_column(String(1024))
    doc_file: Mapped[str | None] = mapped_column(String(1024))
    presentation: Mapped[str | None] = mapped_column(String(1024))
    screencast_file: Mapped[str | None] = mapped_column(String(1024))
    screencast_url: Mapped[str | None] = mapped_column(String(1024))
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus, name="submission_status"),
        default=SubmissionStatus.draft,
        nullable=False,
    )
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    team = relationship("Team", back_populates="submissions")
    hackathon = relationship("Hackathon", back_populates="submissions")
    check_results = relationship("CheckResult", back_populates="submission", cascade="all, delete-orphan")
    expert_scores = relationship("ExpertScore", back_populates="submission", cascade="all, delete-orphan")
