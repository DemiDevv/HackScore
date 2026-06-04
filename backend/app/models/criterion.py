import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Criterion(Base):
    __tablename__ = "criteria"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hackathon_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hackathons.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    is_auto: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order_index: Mapped[int | None] = mapped_column(Integer)

    hackathon = relationship("Hackathon", back_populates="criteria")
    expert_scores = relationship("ExpertScore", back_populates="criterion", cascade="all, delete-orphan")
