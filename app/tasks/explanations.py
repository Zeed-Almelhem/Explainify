from app.core.celery_app import celery_app
from app.core.xai.shap_explainer import SHAPExplainer
import joblib
import numpy as np
from typing import List, Dict, Any
from loguru import logger
import os
from app.core.config import settings

@celery_app.task(name="app.tasks.explanations.generate_explanation")
def generate_explanation(
    model_name: str,
    data_id: str,
    instance_index: int,
    methods: List[str]
) -> Dict[str, Any]:
    """Generate model explanations using specified XAI methods."""
    try:
        # Load model
        model_path = os.path.join(settings.MODEL_STORAGE_PATH, model_name)
        model = joblib.load(model_path)
        
        # Load data
        data_path = os.path.join(settings.DATASET_STORAGE_PATH, f"{data_id}.npz")
        data = np.load(data_path)
        X = data["X"]
        
        results = {}
        
        # Generate explanations for each requested method
        if "shap" in methods:
            explainer = SHAPExplainer()
            results["shap"] = {
                "feature_importance": explainer.explain_feature_importance(model, X),
                "local": explainer.explain_local(model, X, instance_index)
            }
        
        # Add other XAI methods here (LIME, ELI5, etc.)
        
        return results
    except Exception as e:
        logger.error(f"Error generating explanation: {str(e)}")
        raise
