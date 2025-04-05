from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from loguru import logger
import os
from typing import List
import shutil
import pickle
import json
from datetime import datetime

app = FastAPI(title="Explainify")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Default Vite dev server
        "http://localhost:5174",  # Alternative port
        "http://localhost:5175",  # Another alternative port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create storage directories
STORAGE_DIR = "./storage"
MODEL_DIR = os.path.join(STORAGE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# Pre-built models
PREBUILT_MODELS = [
    {
        "id": "iris",
        "name": "Iris Classifier",
        "type": "sklearn",
        "description": "A RandomForest classifier trained on the classic iris dataset.",
        "features": ["sepal_length", "sepal_width", "petal_length", "petal_width"],
        "created_at": "2025-04-04T00:00:00Z"
    }
]

# In-memory storage for models and explanations
models = []
explanations = []

@app.get("/")
async def root():
    """Redirect root to API documentation"""
    return RedirectResponse(url="/docs")

@app.post("/api/v1/models/upload")
async def upload_model(file: UploadFile = File(...)):
    """Upload a machine learning model file"""
    if not file.filename.endswith(('.pkl', '.h5')):
        raise HTTPException(status_code=400, detail="Invalid file format. Only .pkl and .h5 files are supported.")
    
    try:
        # Save the file
        file_path = os.path.join(MODEL_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Add model to the list
        model_id = str(len(models) + 1)
        model = {
            "id": model_id,
            "name": file.filename,
            "type": "sklearn" if file.filename.endswith('.pkl') else "keras",
            "created_at": datetime.now().isoformat()
        }
        models.append(model)
        
        return model
        
    except Exception as e:
        logger.error(f"Error uploading model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/models")
async def list_models():
    """List all uploaded models"""
    return PREBUILT_MODELS + models

@app.post("/api/v1/explanations")
async def generate_explanation(model_id: str, type: str = "feature_importance"):
    """Generate an explanation for a model prediction"""
    try:
        # First check pre-built models
        model = next((m for m in PREBUILT_MODELS if m["id"] == model_id), None)
        if not model:
            # Then check uploaded models
            model = next((m for m in models if m["id"] == model_id), None)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # For pre-built models, use the pre-defined filename
        if model["id"] == "iris":
            model_path = os.path.join(MODEL_DIR, "iris_classifier.pkl")
        else:
            model_path = os.path.join(MODEL_DIR, model["name"])
        
        with open(model_path, "rb") as f:
            loaded_model = pickle.load(f)
        
        # Generate a simple feature importance explanation
        if hasattr(loaded_model, "feature_importances_"):
            feature_names = model.get("features", ["sepal_length", "sepal_width", "petal_length", "petal_width"])
            importances = loaded_model.feature_importances_
            
            explanation = {
                "id": str(len(explanations) + 1),
                "model_id": model_id,
                "type": type,
                "created_at": datetime.now().isoformat(),
                "result": {
                    "feature_importance": dict(zip(feature_names, importances.tolist()))
                }
            }
            explanations.append(explanation)
            return explanation
        else:
            raise HTTPException(status_code=400, detail="Model does not support feature importance")
            
    except Exception as e:
        logger.error(f"Error generating explanation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/explanations")
async def list_explanations():
    """List all generated explanations"""
    return explanations
