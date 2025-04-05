"""
ELI5 explainer adapter for model explanations.
"""
from typing import Any, Dict, List, Optional, Union

import numpy as np
from sklearn.base import BaseEstimator
import tensorflow as tf

from .base import BaseExplainer
from ...schemas.explanation import ExplanationFormat, ExplanationRequest


class ELI5Explainer(BaseExplainer):
    """ELI5 explainer adapter for both sklearn and tensorflow models."""

    def __init__(self):
        """Initialize ELI5 explainer."""
        super().__init__(name="eli5")

    def explain(
        self,
        model: Union[BaseEstimator, tf.keras.Model],
        data: np.ndarray,
        request: ExplanationRequest,
    ) -> Dict[str, Any]:
        """
        Generate explanations using ELI5-like approach.

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
        if request.format == ExplanationFormat.FEATURE_IMPORTANCE:
            # Get feature importances from model if available
            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_
            elif hasattr(model, "coef_"):
                importances = np.abs(model.coef_).mean(axis=0) if len(model.coef_.shape) > 1 else np.abs(model.coef_)
            else:
                raise ValueError("Model does not support feature importance calculation")

            return {
                "method": "eli5",
                "type": "feature_importance",
                "explanation": {
                    "feature_importances": dict(zip(request.feature_names, importances.tolist())),
                },
                "feature_names": request.feature_names,
                "target_names": request.target_names
            }
        else:  # Instance-level explanation
            # For instance-level explanations, we'll calculate feature contributions
            if hasattr(model, "coef_"):
                # For linear models
                contributions = []
                if len(model.coef_.shape) > 1:
                    # Multi-class case
                    for i, target_name in enumerate(request.target_names):
                        feature_contributions = {}
                        for j, feature_name in enumerate(request.feature_names):
                            feature_contributions[feature_name] = float(data[0, j] * model.coef_[i, j])
                        contributions.append({
                            "target": target_name,
                            "contributions": feature_contributions
                        })
                else:
                    # Binary classification or regression
                    feature_contributions = {}
                    for j, feature_name in enumerate(request.feature_names):
                        feature_contributions[feature_name] = float(data[0, j] * model.coef_[0, j])  # Update here
                    contributions.append({
                        "target": request.target_names[0],
                        "contributions": feature_contributions
                    })

                return {
                    "method": "eli5",
                    "type": "instance",
                    "explanation": {
                        "targets": contributions
                    },
                    "feature_names": request.feature_names,
                    "target_names": request.target_names
                }
            else:
                raise ValueError("Model does not support instance-level explanations")

    def _explain_tensorflow(
        self,
        model: tf.keras.Model,
        data: np.ndarray,
        request: ExplanationRequest,
    ) -> Dict[str, Any]:
        """Generate explanations for tensorflow models."""
        if request.format == ExplanationFormat.FEATURE_IMPORTANCE:
            # Get feature importances through permutation
            base_score = model.evaluate(data, verbose=0)[0]  # Get first value from evaluate output
            importances = []
            
            for i in range(data.shape[1]):
                # Create a copy and permute one feature
                permuted_data = data.copy()
                permuted_data[:, i] = np.random.permutation(permuted_data[:, i])
                
                # Calculate importance as decrease in performance
                new_score = model.evaluate(permuted_data, verbose=0)[0]  # Get first value from evaluate output
                importance = abs(base_score - new_score)  # Use absolute difference
                importances.append(importance)
            
            # Normalize importances
            importances = np.array(importances)
            if importances.max() - importances.min() > 0:
                importances = (importances - importances.min()) / (importances.max() - importances.min())
            else:
                importances = np.ones_like(importances) / len(importances)  # Equal importance if no variation
            
            return {
                "method": "eli5",
                "type": "feature_importance",
                "explanation": {
                    "feature_importances": dict(zip(request.feature_names, importances.tolist())),
                },
                "feature_names": request.feature_names,
                "target_names": request.target_names
            }
        else:
            raise ValueError("Instance-level explanations not supported for TensorFlow models")
