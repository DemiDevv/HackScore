import uuid

from pydantic import BaseModel, Field


class CriterionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    weight: float = Field(ge=0, le=1)
    max_score: int = Field(default=10, gt=0, le=100)
    is_auto: bool = False
    order_index: int | None = None


class CriterionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    weight: float | None = Field(default=None, ge=0, le=1)
    max_score: int | None = Field(default=None, gt=0, le=100)
    is_auto: bool | None = None
    order_index: int | None = None


class CriterionWeightUpdate(BaseModel):
    id: uuid.UUID
    weight: float = Field(ge=0, le=1)


class CriteriaWeightsUpdate(BaseModel):
    weights: list[CriterionWeightUpdate] = Field(min_length=1)


class CriterionResponse(BaseModel):
    id: uuid.UUID
    hackathon_id: uuid.UUID
    name: str
    description: str | None
    weight: float
    max_score: int
    is_auto: bool
    order_index: int | None

    model_config = {"from_attributes": True}
