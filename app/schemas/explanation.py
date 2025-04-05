"""
Pydantic models for explanation requests and responses.
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class ExplanationFormat(str, Enum):
    """Supported explanation formats."""

    FEATURE_IMPORTANCE = "feature_importance"
    INSTANCE = "instance"


class ExplanationRequest(BaseModel):
    """Schema for explanation request."""

    format: ExplanationFormat
    feature_names: List[str]
    target_names: List[str]
    instance_index: Optional[int] = None


class ExplanationResponse(BaseModel):
    """Schema for explanation response."""

    method: str
    type: str
    explanation: dict
    feature_names: List[str]
    target_names: List[str]
