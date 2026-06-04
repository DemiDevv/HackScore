import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Text, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import AlgoLanguage, AlgoVerdict


class AlgoTask(Base):
    __tablename__ = "algo_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hackathon_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hackathons.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    time_limit_ms: Mapped[int] = mapped_column(Integer, default=2000, nullable=False)
    memory_limit_mb: Mapped[int] = mapped_column(Integer, default=256, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    hackathon = relationship("Hackathon", back_populates="algo_tasks")
    creator = relationship("User", back_populates="algo_tasks")
    tests = relationship("AlgoTest", back_populates="task", cascade="all, delete-orphan")
    submissions = relationship("AlgoSubmission", back_populates="task", cascade="all, delete-orphan")


class AlgoTest(Base):
    __tablename__ = "algo_tests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("algo_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    input_data: Mapped[str] = mapped_column(Text, nullable=False)
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order_index: Mapped[int | None] = mapped_column(Integer)

    task = relationship("AlgoTask", back_populates="tests")


class AlgoSubmission(Base):
    __tablename__ = "algo_submissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("algo_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
    )
    language: Mapped[AlgoLanguage] = mapped_column(Enum(AlgoLanguage, name="algo_language"), nullable=False)
    source_code: Mapped[str] = mapped_column(Text, nullable=False)
    verdict: Mapped[AlgoVerdict] = mapped_column(
        Enum(AlgoVerdict, name="algo_verdict"),
        default=AlgoVerdict.pending,
        nullable=False,
    )
    execution_time: Mapped[int | None] = mapped_column(Integer)
    memory_used: Mapped[int | None] = mapped_column(Integer)
    test_passed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    test_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    task = relationship("AlgoTask", back_populates="submissions")
    user = relationship("User", back_populates="algo_submissions")
    team = relationship("Team", back_populates="algo_submissions")
