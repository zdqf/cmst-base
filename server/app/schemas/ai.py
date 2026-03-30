"""AI diagnosis Pydantic schemas for API request/response models.

Requirements:
- 4.1: Structured form: age, gender, symptoms, allergy history, current medication
- 4.3: Append disclaimer to AI diagnosis results
- 4.4: Display disclaimer at top of result page
- 4.8: History records in time-descending order
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class DiagnosisRequest(BaseModel):
    """Structured health info form for AI diagnosis (Requirement 4.1)."""

    age: int = Field(..., ge=0, le=200, description="年龄")
    gender: str = Field(..., description="性别")
    symptoms: str = Field(..., min_length=1, description="主要不适描述")
    allergy_history: str = Field(default="", description="既往过敏史")
    current_medication: str = Field(default="", description="当前用药情况")


class DiagnosisResponse(BaseModel):
    """AI diagnosis result (Requirement 4.3)."""

    id: uuid.UUID
    result: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DiagnosisHistoryItem(BaseModel):
    """Single history record for diagnosis list (Requirement 4.8)."""

    id: uuid.UUID
    input_data: dict
    ai_output: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PairingRequest(BaseModel):
    """Request body for herb pairing suggestions (Requirement 5.1)."""

    herb_ids: list[uuid.UUID] = Field(..., min_length=1, description="中药 ID 列表")


class PairingResponse(BaseModel):
    """AI pairing suggestion result (Requirements 5.2, 5.3, 5.4)."""

    result: str = Field(..., description="搭配建议文本")

# ---------------------------------------------------------------------------
# Admin schemas for diagnosis log management (Requirements 10.1, 10.2, 10.3)
# ---------------------------------------------------------------------------


class AdminDiagnosisLogItem(BaseModel):
    """List item for admin diagnosis log view (Requirement 10.1).

    Shows summary info: user_id, time, input/output summaries.
    """

    id: uuid.UUID
    user_id: uuid.UUID
    input_data: dict
    ai_output: str
    prompt_version: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminDiagnosisLogDetail(BaseModel):
    """Full detail view for a single diagnosis log (Requirement 10.2).

    Includes complete input_data and ai_output.
    """

    id: uuid.UUID
    user_id: uuid.UUID
    input_data: dict
    ai_output: str
    prompt_version: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

