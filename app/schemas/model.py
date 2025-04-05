from enum import Enum
from pydantic import BaseModel

class ModelType(str, Enum):
    SKLEARN = "sklearn"
    XGBOOST = "xgboost"
    TENSORFLOW = "tensorflow"

class ModelInfo(BaseModel):
    name: str
    type: ModelType
    path: str
