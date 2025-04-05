from fastapi import FastAPI, HTTPException, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from loguru import logger
import os
from typing import List, Dict, Union
import shutil
import pickle
import json
from datetime import datetime
import numpy as np
from pydantic import BaseModel

class ExplanationRequest(BaseModel):
    model_id: str
    type: str
    input_data: Dict[str, float]

app = FastAPI(title="Explainify")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Default Vite dev server
        "http://localhost:5174",  # Alternative port
        "http://localhost:5175",  # Another alternative port
        "http://localhost:5176",
        "http://localhost:5177",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
        "http://127.0.0.1:5177",
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
        
        # Try to load the model to get features
        with open(file_path, "rb") as f:
            model = pickle.load(f)
        
        # Extract features if available
        features = []
        if hasattr(model, 'feature_names_in_'):
            features = model.feature_names_in_.tolist()
        
        # Add model to the list
        model_id = str(len(models) + 1)
        model_info = {
            "id": model_id,
            "name": file.filename,
            "type": "sklearn" if file.filename.endswith('.pkl') else "keras",
            "features": features,
            "created_at": datetime.now().isoformat()
        }
        models.append(model_info)
        
        return model_info
        
    except Exception as e:
        logger.error(f"Error uploading model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/models")
async def list_models():
    """List all uploaded models"""
    return PREBUILT_MODELS + models

@app.post("/api/v1/explanations")
async def generate_explanation(request: ExplanationRequest):
    """Generate an explanation for a model prediction"""
    try:
        # First check pre-built models
        model = next((m for m in PREBUILT_MODELS if m["id"] == request.model_id), None)
        if not model:
            # Then check uploaded models
            model = next((m for m in models if m["id"] == request.model_id), None)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # For pre-built models, use the pre-defined filename
        if model["id"] == "iris":
            model_path = os.path.join(MODEL_DIR, "iris_classifier.pkl")
        else:
            model_path = os.path.join(MODEL_DIR, model["name"])
        
        with open(model_path, "rb") as f:
            loaded_model = pickle.load(f)
        
        # Prepare input data
        features = model.get("features", ["sepal_length", "sepal_width", "petal_length", "petal_width"])
        input_array = np.array([[request.input_data[f] for f in features]])
        
        # Generate prediction
        prediction = None
        prediction_proba = None
        if hasattr(loaded_model, 'predict'):
            prediction = loaded_model.predict(input_array)[0]
        if hasattr(loaded_model, 'predict_proba'):
            prediction_proba = loaded_model.predict_proba(input_array)[0].tolist()
        
        # Generate explanation based on type
        result = {}
        
        # Feature importance
        if hasattr(loaded_model, "feature_importances_"):
            result["feature_importance"] = dict(zip(features, loaded_model.feature_importances_.tolist()))
        
        # Add prediction results
        if prediction is not None:
            result["prediction"] = prediction
        if prediction_proba is not None:
            result["prediction_probabilities"] = prediction_proba
            
        # Add input data for reference
        result["input_data"] = request.input_data
            
        explanation = {
            "id": str(len(explanations) + 1),
            "model_id": request.model_id,
            "type": request.type,
            "created_at": datetime.now().isoformat(),
            "result": result
        }
        explanations.append(explanation)
        return explanation
            
    except Exception as e:
        logger.error(f"Error generating explanation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/explanations")
async def list_explanations(model_id: str = None):
    """List all generated explanations, optionally filtered by model_id"""
    if model_id:
        return [e for e in explanations if e["model_id"] == model_id]
    return explanations
