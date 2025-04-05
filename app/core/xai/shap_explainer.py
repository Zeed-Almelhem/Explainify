"""
SHAP explainer implementation.
"""
from typing import Any, Dict, Union
import numpy as np
from sklearn.base import BaseEstimator
import tensorflow as tf
import shap

from .base import BaseExplainer
from ...schemas.explanation import ExplanationRequest


class SHAPExplainer(BaseExplainer):
    """SHAP explainer adapter."""

    def __init__(self):
        """Initialize SHAP explainer."""
        super().__init__(name="shap")

    def explain(
        self,
        model: Union[BaseEstimator, tf.keras.Model],
        data: np.ndarray,
        request: ExplanationRequest,
    ) -> Dict[str, Any]:
        """
        Generate explanations using SHAP.

        Args:
            model: The trained model to explain (sklearn or tensorflow)
            data: Input data to explain
            request: ExplanationRequest containing parameters

        Returns:
            Dict containing explanation data
        """
        try:
            if isinstance(model, tf.keras.Model):
                return self._explain_tensorflow(model, data, request)
            else:
                return self._explain_sklearn(model, data, request)
        except Exception as e:
            raise ValueError(f"Failed to generate explanation: {str(e)}")

    def _explain_sklearn(
        self,
        model: BaseEstimator,
        data: np.ndarray,
        request: ExplanationRequest,
    ) -> Dict[str, Any]:
        """Generate explanations for sklearn models."""
        # Create a background dataset for the explainer
        if len(data) > 1:
            background = data[:10]  # Use first 10 samples as background
        else:
            background = data  # Use the single instance as background

        # Create explainer based on model type
        if hasattr(model, "predict_proba"):
            explainer = shap.KernelExplainer(
                lambda x: model.predict_proba(x)[:, 1] if x.shape[0] else np.array([]),
                background
            )
        else:
            explainer = shap.KernelExplainer(model.predict, background)

        # Get SHAP values
        shap_values = explainer.shap_values(data)

        if request.format == "feature_importance":
            # Global feature importance
            importances = np.abs(shap_values).mean(axis=0) if len(shap_values.shape) > 1 else np.abs(shap_values)
            return {
                "method": "shap",
                "type": "feature_importance",
                "explanation": {
                    "feature_importances": dict(zip(request.feature_names, importances.tolist())),
                },
                "feature_names": request.feature_names,
                "target_names": request.target_names
            }
        else:
            # Instance-level explanation
            return {
                "method": "shap",
                "type": "instance",
                "explanation": {
                    "shap_values": shap_values.tolist(),
                    "expected_value": float(explainer.expected_value)
                },
                "feature_names": request.feature_names,
                "target_names": request.target_names
            }

    def _explain_tensorflow(
        self,
        model: tf.keras.Model,
        data: np.ndarray,
        request: ExplanationRequest,
    ) -> Dict[str, Any]:
        """Generate explanations for tensorflow models."""
        # Create a background dataset for the explainer
        if len(data) > 1:
            background = data[:10]  # Use first 10 samples as background
        else:
            background = data  # Use the single instance as background

        # Create explainer
        explainer = shap.KernelExplainer(model.predict, background)
        shap_values = explainer.shap_values(data)

        if request.format == "feature_importance":
            # Global feature importance
            importances = np.abs(shap_values).mean(axis=0) if len(np.array(shap_values).shape) > 1 else np.abs(shap_values)
            return {
                "method": "shap",
                "type": "feature_importance",
                "explanation": {
                    "feature_importances": dict(zip(request.feature_names, importances.tolist())),
                },
                "feature_names": request.feature_names,
                "target_names": request.target_names
            }
        else:
            # Instance-level explanation
            return {
                "method": "shap",
                "type": "instance",
                "explanation": {
                    "shap_values": shap_values.tolist() if isinstance(shap_values, np.ndarray) else shap_values[0].tolist(),
                    "expected_value": float(explainer.expected_value[0]) if isinstance(explainer.expected_value, list) else float(explainer.expected_value)
                },
                "feature_names": request.feature_names,
                "target_names": request.target_names
            }
