from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import joblib
import os
from app.core.config import settings
from app.schemas.model import ModelInfo, ModelType
from loguru import logger

router = APIRouter()

@router.post("/upload", response_model=ModelInfo)
async def upload_model(
    model_file: UploadFile = File(...),
    model_type: ModelType = ModelType.SKLEARN
):
    """Upload a trained ML model."""
    try:
        # Create storage directory if it doesn't exist
        os.makedirs(settings.MODEL_STORAGE_PATH, exist_ok=True)
        
        # Save model file
        model_path = os.path.join(settings.MODEL_STORAGE_PATH, model_file.filename)
        with open(model_path, "wb") as f:
            content = await model_file.read()
            f.write(content)
        
        # Load model to verify it's valid
        model = joblib.load(model_path)
        
        return ModelInfo(
            name=model_file.filename,
            type=model_type,
            path=model_path
        )
    except Exception as e:
        logger.error(f"Error uploading model: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/list", response_model=List[ModelInfo])
async def list_models():
    """List all uploaded models."""
    try:
        models = []
        for filename in os.listdir(settings.MODEL_STORAGE_PATH):
            if filename.endswith('.joblib') or filename.endswith('.pkl'):
                models.append(
                    ModelInfo(
                        name=filename,
                        type=ModelType.SKLEARN,  # This is a simplification
                        path=os.path.join(settings.MODEL_STORAGE_PATH, filename)
                    )
                )
        return models
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
