from typing import Any, Dict
import numpy as np
import shap
from .base import XAIExplainer

class SHAPExplainer(XAIExplainer):
    """SHAP-based model explanation adapter."""
    
    def __init__(self):
        self.explainer = None
    
    def _init_explainer(self, model: Any, X: np.ndarray):
        if self.explainer is None:
            self.explainer = shap.Explainer(model, X)
    
    def explain_feature_importance(self, model: Any, X: np.ndarray) -> Dict[str, Any]:
        self._init_explainer(model, X)
        shap_values = self.explainer(X)
        
        return {
            "method": "shap",
            "global_importance": shap_values.abs.mean(0).values.tolist(),
            "feature_names": self.explainer.feature_names
        }
    
    def explain_local(self, model: Any, X: np.ndarray, instance_index: int) -> Dict[str, Any]:
        self._init_explainer(model, X)
        instance = X[instance_index:instance_index+1]
        shap_values = self.explainer(instance)
        
        return {
            "method": "shap",
            "local_importance": shap_values[0].values.tolist(),
            "feature_names": self.explainer.feature_names,
            "base_value": float(shap_values.base_values[0])
        }
    
    def explain_counterfactual(self, model: Any, X: np.ndarray, instance_index: int) -> Dict[str, Any]:
        raise NotImplementedError("SHAP does not directly support counterfactual explanations")
    
    def get_influential_examples(self, model: Any, X: np.ndarray, instance_index: int) -> Dict[str, Any]:
        raise NotImplementedError("SHAP does not directly support influential example identification")
