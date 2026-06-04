import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import AlgoLanguage, AlgoVerdict


class AlgoTaskCreate(BaseModel):
    hackathon_id: uuid.UUID
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    time_limit_ms: int = Field(default=2000, gt=0, le=30000)
    memory_limit_mb: int = Field(default=256, gt=0, le=2048)


class AlgoTestCreate(BaseModel):
    input_data: str
    expected_output: str
    is_sample: bool = False
    order_index: int | None = None


class AlgoTestResponse(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    input_data: str
    expected_output: str
    is_sample: bool
    order_index: int | None

    model_config = {"from_attributes": True}


class AlgoTaskResponse(BaseModel):
    id: uuid.UUID
    hackathon_id: uuid.UUID
    title: str
    description: str
    time_limit_ms: int
    memory_limit_mb: int
    created_by: uuid.UUID
    tests: list[AlgoTestResponse] = []

    model_config = {"from_attributes": True}


class AlgoSubmitRequest(BaseModel):
    language: AlgoLanguage
    source_code: str = Field(min_length=1)


class AlgoSubmissionResponse(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    user_id: uuid.UUID
    team_id: uuid.UUID
    language: AlgoLanguage
    source_code: str
    verdict: AlgoVerdict
    execution_time: int | None
    memory_used: int | None
    test_passed: int
    test_total: int
    error_message: str | None
    submitted_at: datetime

    model_config = {"from_attributes": True}
